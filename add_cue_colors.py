import os
import argparse
import csv
import xml
import xml.etree.ElementTree as ET

counter = 0
output_file = "../VDJ/execution.log"

def add_color(line):
    xml_line = ET.fromstring(line)

    if xml_line.get("Name").lower().startswith("intro") :
        xml_line.set("Color", "4294934272") # orange
    elif xml_line.get("Name").lower().startswith("verse") :
        xml_line.set("Color", "4278190335") # blue
    elif xml_line.get("Name").lower().startswith("chorus") :
        xml_line.set("Color", "4294901760") # red
    elif xml_line.get("Name").lower().startswith("hook") :
        xml_line.set("Color", "4294901760") # red
    elif xml_line.get("Name").lower().startswith("bridge") :
        xml_line.set("Color", "4288020735") # violet
    elif xml_line.get("Name").lower().startswith("break") :
        xml_line.set("Color", "4294967040") # yellow
    elif xml_line.get("Name").lower().startswith("beat") and xml_line.get("Name") != "Beat Marker" :
        xml_line.set("Color", "4278255360") # green

    # rearrange
    if "Color" in xml_line.attrib:
        xml_line = ET.Element("Poi", attrib={'Name': xml_line.attrib['Name'], 'Pos': xml_line.attrib['Pos'], 'Num': xml_line.attrib['Num'], 'Color': xml_line.attrib['Color'], 'Type': xml_line.attrib['Type']})
    else :
        xml_line = ET.Element("Poi", attrib={'Name': xml_line.attrib['Name'], 'Pos': xml_line.attrib['Pos'], 'Num': xml_line.attrib['Num'], 'Type': xml_line.attrib['Type']})

    return ET.tostring(xml_line, encoding='unicode')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help = "Enter your variable")
    args = parser.parse_args()

    if args.path:
        print(f"Received variable value from command line: {args.path}")

        global counter

        # Open the file and read line by line
        with open(args.path, 'r', encoding='utf-8') as file:
            all_lines = file.readlines()

            with open(args.path, 'w', encoding='utf-8') as edit :

                with open(output_file, mode='w', newline='') as output:
                    execution_log = csv.DictWriter(output, fieldnames=["counter","old","new"])
                    execution_log.writeheader()

                    for i, line in enumerate(all_lines) :

                        if "Poi" in line and "Name=" in line and "Pos=" in line and "Num=" in line and "Type=" in line and "n.n." not in line :
                            colored_line = add_color(line)
                            execution_log.writerow({"counter": counter, "old": line.strip(), "new": colored_line})
                            all_lines[i] = "  " + colored_line + '\n'
                        else :
                            all_lines[i] = line

                        counter+=1

                edit.writelines(all_lines)

    else:
        print("No variable received from command line.")

if __name__ == "__main__":
    main()