import bottle
from Database import Database



class WebServer(bottle.Bottle):

    def __init__(self):
        self.database = Database()

        self.route("/upload", method="POST", callback=self.upload)


    def upload(self):
        marketdata = bottle.request.files.get("Commodities.json")
        return ""



if __name__ == "__main__":
    bottle.run(host="localhost", port=80)
