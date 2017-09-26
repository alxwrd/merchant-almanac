import json

import bottle
from Almanac import Almanac



class WebServer(bottle.Bottle):

    def __init__(self):
        super().__init__()
        self.almanac = Almanac()

        self.route("/upload", method="POST", callback=self.upload)


    def upload(self):
        marketdata = bottle.request.files.get("Commodities.json")

        self.almanac.update(json.loads(marketdata.file.read().decode("utf-8")))
        return ""



if __name__ == "__main__":
    app = WebServer()
    bottle.run(app, host="localhost", port=80)
