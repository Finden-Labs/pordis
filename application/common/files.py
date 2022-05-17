import os

class Files:
    def ReadListFile(path):
        lines = []
        if not os.path.exists(path):
            return lines
        with open(path) as f:
            lines = f.readlines()
            lines = [line.rstrip() for line in lines if line[0] != "#"]
        return lines
    
    def WriteListFile(path, list):
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), 0o777, True)
        with open(path, "w") as f:
            f.writelines(list)

    def ReadIniFile(path):
        data = {}
        if not os.path.exists(path):
            return data

        with open(path, "r") as f:
            lines = f.read().split("\n")
            for line in lines:
                if not "=" in line:
                    continue
                data[line.split("=")[0]] = line.split("=")[1]
        
        return data
    
    def WriteIniFile(path, dict):
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), 0o777, True)
        with open(path, "w") as f:
            for k, v in dict.items():
                f.write(k + "=" + v + "\n")
            f.write("\n")
