from website import create_app

# we can import it because website is a python package

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
