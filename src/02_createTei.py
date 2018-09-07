import uuid
import xml.etree.ElementTree as ET
import json
import requests
import urllib
import csv
import uuid


def exec2canvas(root, json_data, canvas, image):
    surfaceGrp = root.find(prefix + "surfaceGrp")

    surface = ET.Element("{http://www.tei-c.org/ns/1.0}surface")
    surfaceGrp.append(surface)

    graphic = ET.Element("{http://www.tei-c.org/ns/1.0}graphic")
    surface.append(graphic)
    graphic.set("url", image)
    graphic.set("n", canvas)

    body = root.find(prefix + "body")

    p = ET.Element("{http://www.tei-c.org/ns/1.0}p")
    body.append(p)

    # for element in json_data:
    for i in range(1, len(json_data)):
        element = json_data[i]
        text = element["description"];
        array = element["boundingPoly"]["vertices"]
        ulx = 10000000000
        uly = 10000000000
        lrx = 0
        lry = 0
        for area in array:
            if "x" in area:
                x = int(area["x"])

                if x >= 0:

                    if x < ulx:
                        ulx = x

                    if x > lrx:
                        lrx = x

            if "y" in area:
                y = int(area["y"])

                if y >= 0:

                    if y < uly:
                        uly = y

                    if y > lry:
                        lry = y

        zone_id = "zone_" + str(uuid.uuid1())

        zone = ET.Element("{http://www.tei-c.org/ns/1.0}zone")
        surface.append(zone)
        zone.set("xml:id", zone_id)
        zone.set("lry", str(lry))
        zone.set("lrx", str(lrx))
        zone.set("uly", str(uly))
        zone.set("ulx", str(ulx))

        span = ET.Element("{http://www.tei-c.org/ns/1.0}span")
        p.append(span)
        span.set("facs", "#" + zone_id)
        span.text = text


if __name__ == "__main__":

    inputpath = "data/manifest_list.csv"
    inputdir = "json"
    outputdir = "../docs/xml"
    tmp_path = "data/template.xml"

    with open(inputpath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # ヘッダーを読み飛ばしたい時

        for row in reader:
            oid = row[2]
            manifest_url = row[3]

            if manifest_url == "":
                continue

            prefix = ".//{http://www.tei-c.org/ns/1.0}"
            xml = ".//{http://www.w3.org/XML/1998/namespace}"

            tree = ET.parse(tmp_path)
            ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
            root = tree.getroot()

            res = urllib.request.urlopen(manifest_url)
            # json_loads() でPythonオブジェクトに変換
            manifest = json.loads(res.read().decode('utf-8'))

            canvases = manifest["sequences"][0]["canvases"]

            try:
                # ローカルJSONファイルの読み込み
                with open(inputdir + "/" + str(oid) + ".json", 'r') as f:
                    data = json.load(f)

                    for i in range(len(data)):

                        if i % 5 == 0:
                            print(str(i) + "/" + str(len(canvases)))

                        canvas = canvases[i]
                        canvas_id = canvas["@id"]
                        image_path = canvas["images"][0]["resource"]["@id"]

                        if ".jpg" not in image_path:
                            image_path = image_path + "/full/,800/0/default.jpg"

                        exec2canvas(root, data[i], canvas_id, image_path)
            except json.JSONDecodeError as e:
                print('JSONDecodeError: ', e)

            surfaceGrp = root.find(prefix + "surfaceGrp")
            surfaceGrp.set("facs", manifest_url)

            title = root.find(prefix + "title")
            title.text = manifest["label"]

            metadata = manifest["metadata"]

            ident = None
            relation = None

            for m in metadata:
                if m["label"] == "Identifier":
                    ident = m["value"]
                    relation = "http://dch.iii.u-tokyo.ac.jp/omekas2/s/dch/record/" + ident

                    break

            if uuid != None:
                sourceDesc = root.find(prefix + "sourceDesc")
                p = ET.Element("{http://www.tei-c.org/ns/1.0}p")
                sourceDesc.append(p)

                ref = ET.Element("{http://www.tei-c.org/ns/1.0}ref")
                p.append(ref)

                ref.set("target", relation)
                ref.text = relation

                tree.write(outputdir + "/" + ident + ".xml", encoding="utf-8")
            else:
                print(manifest_url)
