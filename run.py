from app import create_app

app = create_app()

if __name__ == "__main__":
    # Use this line for deployment purposes
    # app.run(host="0.0.0.0", port=80, debug=False)

    # Use this line for local debugging purposes
    app.run(host="0.0.0.0", debug=True)

