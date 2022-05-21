import xml.etree.ElementTree as ET
import json
import os


EnvironmentFile = "../Resource/LucyLua/WebEnvironment.xml"
PatchSettingFile = "../Resource/LucyLua/PatchSetting.json"
PatchSettingFile01 = "../Resource/LucyLua/"

BuildCmd = "./gradlew assemble"
BuildSetting = [
	{
		"BuildName":"MmDebug", 			
		"outputPath": "./build/outputs/apk/mm/debug",
		"PatchSetting": {
			"MARKETING_CHANNEL":"official",
			"REGION_CHANNEL": "MM",
		}
	}
	,
	{
		"BuildName":"MmDebug", 			
		"outputPath": "./build/outputs/apk/mm/debug",
		"PatchSetting": {
			"MARKETING_CHANNEL":"google",
			"REGION_CHANNEL": "MM",
		}
	}
	,
	{
		"BuildName":"MmRelease", 			
		"outputPath": "./build/outputs/apk/mm/release",
		"PatchSetting": {
			"MARKETING_CHANNEL": "official",
			"REGION_CHANNEL": "MM",
		}
	}
	,
	{
		"BuildName":"MmRelease", 			
		"outputPath": "./build/outputs/apk/mm/release",
		"PatchSetting": {
			"MARKETING_CHANNEL": "google",
			"REGION_CHANNEL": "MM",
		}
	}
	,
	{
		"BuildName":"ThDebug", 			
		"outputPath": "./build/outputs/apk/th/debug",
		"PatchSetting": {
			"MARKETING_CHANNEL": "official",
			"REGION_CHANNEL": "TH",
		}
	}
	,
	{
		"BuildName":"ThRelease", 			
		"outputPath": "./build/outputs/apk/th/release",
		"PatchSetting": {
			"MARKETING_CHANNEL": "official",
			"REGION_CHANNEL": "TH",
		}
	},
	{
		"BuildName":"Fhm_playstoreDebug", 	
		"outputPath": "./build/outputs/apk/fhm_playstore/debug",
		"PatchSetting": {
			"MARKETING_CHANNEL": "playStore",
			"REGION_CHANNEL": "TH",
		}
	}
	,
	{
		"BuildName":"Fhm_playstoreRelease",
		"outputPath": "./build/outputs/apk/fhm_playstore/release",
		"PatchSetting": {
			"MARKETING_CHANNEL": "playStore",
			"REGION_CHANNEL": "TH",
		}
	}
]

# X個環境, 以及變換環境時需要更動的參數
EnvironmentSetting = ["testing", "production"]
EnvironmentPatchSetting = {
	"testing" : {
		"PREPATCH_ENABLE": 1,
		"CDN_SITE":	"http://35.240.204.1/FHM99/Android/cdnSite/",
		"CHECKVERSION_SITE":"http://35.240.204.1/FHM99/Android/"
	}
	,
	"production" : {
		"PREPATCH_ENABLE": 1,
		"CDN_SITE":	"https://patch.fhm99.com/FHM99/Android/cdnSite/",
		"CHECKVERSION_SITE":"https://patch.fhm99.com/FHM99/Android/"
	}
}

count = 1

# 更動 WebEnvironment.xml
def EditEnvironmentXml(typeName:str):
	print("\n\tchange to[", typeName, "]Environment")
	tree = ET.parse(EnvironmentFile)
	root = tree.getroot()

	# 尋找 type 節點
	for _type in root.iter('type'):
	    _type.text = typeName

	# 寫入 XML 檔案
	# 引數1：xml檔案生成的位置和名字，引數2：指定xml編碼，引數3：xml 宣言，
    # xml 宣言即：是否有 <?xml version='1.0' encoding='utf-8'?>
	tree.write(EnvironmentFile, encoding="utf-8", xml_declaration=True)

# 更動 PatchSetting.json
def EditPatchSettingJson(data:dict):
	content = {}
	# 讀取 PatchSetting.json
	file = open(PatchSettingFile,"r")

	content = json.load(file)

	# 更改 PatchSetting.json 內的值
	for key, value in data.items():
		print("\t",key, ":",content[key], '->', value)
		if content[key]:
			content[key] = value

	file.close()

	# 寫入 PatchSetting.json
	with open(PatchSettingFile,"w") as file:
	    json.dump(content, file, indent=2) 	

# 更改環境時用
def ChangeEnvironment(typeName:str):
	EditEnvironmentXml(typeName)
	EditPatchSettingJson(EnvironmentPatchSetting[typeName])
	

def main():
	cmdStr = ""
	count = 1
	for buildSetting in BuildSetting:
		print("No.",count,":")
		EditPatchSettingJson(buildSetting['PatchSetting'])
		for envir in EnvironmentSetting:
			ChangeEnvironment(envir)

			cmdStr = BuildCmd + buildSetting['BuildName']
			print("\tcmd:", cmdStr)
			
			count += 1

if __name__ == '__main__':
	main()