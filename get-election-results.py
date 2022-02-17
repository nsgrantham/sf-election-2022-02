import json
import csv
import os

# from io import BytesIO
# from urllib.request import urlopen
# from zipfile import ZipFile


# def download_and_unzip(url, dir_):
#     with urlopen(url) as r:
#         with ZipFile(BytesIO(r.read())) as f:
#             f.extractall(dir_)


def read_manifest(filepath, key="Id", value="Description"):
    results = {}
    with open(filepath) as f:
        data = json.load(f)
        for item in data["List"]:
            results[item[key]] = item[value]
    return results


def write_csv(dicts, filepath):
    with open(filepath, "w") as f:
        writer = csv.DictWriter(f, dicts[0].keys())
        writer.writeheader()
        writer.writerows(dicts)


def parse_ballots(dir_):
    contests = read_manifest(os.path.join(dir_, "ContestManifest.json"))
    districts = read_manifest(os.path.join(dir_, "DistrictManifest.json"))
    candidates = read_manifest(os.path.join(dir_, "CandidateManifest.json"))
    tabulators = read_manifest(os.path.join(dir_, "TabulatorManifest.json"))
    ballot_types = read_manifest(os.path.join(dir_, "BallotTypeManifest.json"))
    counting_groups = read_manifest(os.path.join(dir_, "CountingGroupManifest.json"))
    precinct_portions = read_manifest(os.path.join(dir_, "PrecinctPortionManifest.json"))
    voting_locations = read_manifest(
        os.path.join(dir_, "TabulatorManifest.json"),
        value="VotingLocationName"
    )
    district_mapping = read_manifest(
        os.path.join(dir_, "DistrictPrecinctPortionManifest.json"),
        key="PrecinctPortionId",
        value="DistrictId"
    )

    ballots = []
    cvr_exports = [file for file in os.listdir(dir_) if file.startswith("CvrExport_")]

    for cvr_export in cvr_exports:
        with open(os.path.join(dir_, cvr_export)) as f:
            data = json.load(f)
            for session in data["Sessions"]:
                original = session["Original"]
                card = original["Cards"][0]  # should only ever be one "card" per ballot
                ballot = {
                    "tabulator": tabulators[session["TabulatorId"]],
                    "voting_location": voting_locations[session["TabulatorId"]],
                    "counting_group": counting_groups[session["CountingGroupId"]],
                    "precinct_portion": precinct_portions[original["PrecinctPortionId"]],
                    "district": districts[district_mapping[original["PrecinctPortionId"]]],
                    "ballot_type": ballot_types[original["BallotTypeId"]]
                }

                for contest in card["Contests"]:
                    marks = contest["Marks"]
                    contest_key = contests[contest["Id"]].lower().replace('-', '_').replace(' ', '_')
                    ballot[contest_key] = ""
                    if contest["Overvotes"]:
                        continue  # skip contests where a voter voted more than once
                    if marks:
                        mark = marks[0]  # only one mark per contest because no ranked choice voting this election
                        if mark["IsVote"]:
                            ballot[contest_key] = candidates[mark["CandidateId"]]

                ballots.append(ballot)

    return ballots


if __name__ == "__main__":
    # # Download from the following url and save as "data".
    # # Unfortunately I get a 403 forbidden error when trying
    # # to download the zipfile with python. Instead, visit the
    # # url, download it, unzip it, and move the folder to your
    # # working directory.
    # download_and_unzip("https://www.sfelections.org/results/20220215/data/20220215_3/CVR_Export_20220215223514.zip", "data")
    ballots = parse_ballots("data")
    ballots = sorted(ballots, key=len, reverse=True)
    write_csv(ballots, "ballots.csv")
