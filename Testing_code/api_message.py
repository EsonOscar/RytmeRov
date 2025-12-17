from flask import request, jsonify, flash

@app.route("/api/message", methods=["POST"])
@login_required
#@sysadmin_required
def mark_message_read():
    print(
        f"Mark message read API endpoint hit, requested by user: [{current_user.name}] ({current_user.name} {current_user.lastname})"
    )

    message_id = request.args.get("msg_id")

    print(f"Message ID: {message_id}")

    try:
        conn = db_connect()
        conn.execute("UPDATE contact SET is_read = 1 WHERE id = ?", (message_id))
        conn.commit()
        print(f"Message with ID {message_id} marked as read")
    except Exception as e:
        print(f"Database error: {e}")
        flash("Oh no, explosion")
        return jsonify({"Success": False, "Message": "Database error"}), 500
        finally:
            conn.close()

                return (
                    jsonify(
                        {"Success": True, "Message": "API endpoint hit, message marked as read"}
                    ),
                200,
            )