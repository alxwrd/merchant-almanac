import json

import bottle
from Almanac import Almanac


bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024 #100MB


class WebServer(bottle.Bottle):

    def __init__(self):
        super().__init__()
        self.almanac = Almanac()

        self.route("/upload", method="POST", callback=self.upload)

        self.route("/", method="GET", callback=self.index)
        self.route("/almanac/<ocean>", method="GET", callback=self.oceans)
        self.route("/almanac/<ocean>/commodity/<commodity>", method="GET", callback=self.ocean_commodities)
        self.route("/almanac/<ocean>/island/<island>", method="GET", callback=self.islands)
        self.route("/almanac/<ocean>/island/<island>/commodity/<commodity>", method="GET", callback=self.island_commodities)

        #Static files
        self.route("/css/<name>", method='GET',
                   callback=lambda name: bottle.static_file(name, root="./site/css"))
        self.route("/js/<name>", method='GET',
                   callback=lambda name: bottle.static_file(name, root="./site/js"))
        self.route("/img/<name>", method='GET',
                   callback=lambda name: bottle.static_file(name, root="./site/img"))


    def upload(self):
        self.almanac.update(bottle.request.json)
        return ""


    def index(self):
        return bottle.template("site/index.html", almanac=self.almanac)


    def oceans(self, ocean):
        return bottle.template(
            "site/ocean.html",
            ocean=self.almanac.oceans[ocean])


    def islands(self, ocean, island):
        return bottle.template(
            "site/island.html",
            island=self.almanac.oceans[ocean].islands[island])


    def ocean_commodities(self, ocean, commodity):
        return bottle.template(
            "site/commodity.html",
            commodity=self.almanac.oceans[ocean].commodities[commodity])


    def island_commodities(self, ocean, island, commodity):
        return bottle.template(
            "site/commodity.html",
            commodity=self.almanac.oceans[ocean].islands[island].commodities[commodity])

if __name__ == "__main__":
    app = WebServer()
    bottle.run(app, host="localhost", port=80)
