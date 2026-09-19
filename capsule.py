from datetime import datetime, timezone, timedelta

from database import get_connection
from crypto import (
    generate_salt,
    encrypt_message,
    decrypt_message
)


MAX_ATTEMPTS = 5
LOCK_MINUTES = 1


def create_capsule(title, message, unlock_time, password):

    salt = generate_salt()

    encrypted_message = encrypt_message(
        message,
        password,
        salt
    )

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO capsules (
            title,
            encrypted_message,
            salt,
            unlock_time,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        encrypted_message,
        salt,
        unlock_time,
        created_at
    ))

    connection.commit()

    capsule_id = cursor.lastrowid

    connection.close()

    return capsule_id


def get_capsule(capsule_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM capsules
        WHERE id = ?
    """, (capsule_id,))

    capsule = cursor.fetchone()

    connection.close()

    return capsule


def get_all_capsules():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            unlock_time,
            created_at,
            failed_attempts,
            locked_until
        FROM capsules
        ORDER BY unlock_time ASC
    """)

    capsules = cursor.fetchall()

    connection.close()

    return capsules


def delete_capsule(capsule_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM capsules
        WHERE id = ?
    """, (capsule_id,))

    connection.commit()

    connection.close()


def is_unlocked(unlock_time):

    unlock_datetime = datetime.fromisoformat(
        unlock_time
    )

    current_datetime = datetime.now()

    return current_datetime >= unlock_datetime


def get_remaining_time(unlock_time):

    unlock_datetime = datetime.fromisoformat(
        unlock_time
    )

    current_datetime = datetime.now()

    difference = unlock_datetime - current_datetime

    if difference.total_seconds() <= 0:
        return 0

    return int(
        difference.total_seconds()
    )


def is_password_locked(capsule):

    if not capsule["locked_until"]:
        return False

    locked_until = datetime.fromisoformat(
        capsule["locked_until"]
    )

    return datetime.now() < locked_until


def open_capsule(capsule_id, password):

    capsule = get_capsule(capsule_id)

    if capsule is None:
        return None, "Capsule not found."

    if not is_unlocked(
        capsule["unlock_time"]
    ):
        return None, "This capsule is still locked."


    if is_password_locked(capsule):

        return None, (
            "Too many incorrect attempts. "
            "Try again later."
        )


    message = decrypt_message(
        capsule["encrypted_message"],
        password,
        capsule["salt"]
    )


    if message is None:

        connection = get_connection()

        cursor = connection.cursor()

        attempts = capsule["failed_attempts"] + 1

        if attempts >= MAX_ATTEMPTS:

            locked_until = (
                datetime.now()
                + timedelta(minutes=LOCK_MINUTES)
            ).isoformat()

            cursor.execute("""
                UPDATE capsules
                SET failed_attempts = 0,
                    locked_until = ?
                WHERE id = ?
            """, (
                locked_until,
                capsule_id
            ))

        else:

            cursor.execute("""
                UPDATE capsules
                SET failed_attempts = ?
                WHERE id = ?
            """, (
                attempts,
                capsule_id
            ))

        connection.commit()

        connection.close()

        return None, "Incorrect password."

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE capsules
        SET failed_attempts = 0,
            locked_until = NULL
        WHERE id = ?
    """, (capsule_id,))

    connection.commit()

    connection.close()

    return message, None