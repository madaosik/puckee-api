from app import create_app

app = create_app()

if __name__ == "__main__":
    # app.run(template_folder='webapp/templates', debug=True)
    # app.run(host="0.0.0.0", debug=True)
    app.run(host="0.0.0.0", port=80)
    #app.run(host="0.0.0.0", debug=True)

