from app.app import main


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print(e)
            continue
    #main()
