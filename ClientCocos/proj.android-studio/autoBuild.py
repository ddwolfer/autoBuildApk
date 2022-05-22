import xml.etree.ElementTree as ET
import json
import os
import argparse
import time
import shutil
from humanfriendly import format_timespan
from enum import Enum

# 取得cmd參數的值
parser = argparse.ArgumentParser(description='')

# parser.add_argument('--CMD上參數名字', dest='取用變數名稱', type = 型態, default=預設值, help=打help時看到的提示)
# 範例->parser.add_argument('--fileName', dest='fileName', type = str, default='temp.txt', help='output file name')
parser.add_argument('--need_check', dest='needCheck', default=False, action='store_true',help='need check information before every apk build')

args = parser.parse_args()
# args.fileName 可以取到範例的值

# setting Start
SuccessStr = "BUILD SCCESSFUL"
ThreadFailStr = "thread"
BuildCmdStr = "./gradlew assemble"
class BUILD_CODE(Enum):
	SUCCESS = 1
	Thread_Failed = 2
	Unknown_Failed = 99

# Path
EnvironmentFile = "../Resource/LucyLua/WebEnvironment.xml"
PatchSettingFile = "../Resource/LucyLua/PatchSetting.json"
PatchSettingFile01 = "../Resource/LucyLua/"

# 主要為了切換android studio 的varible
# MARKETING_CHANNEL 也寫的原因是 95 98 的名字不一樣
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
# setting End

# 更動 WebEnvironment.xml
def EditEnvironmentXml(typeName:str):
	print("\tchange to [", typeName, "] Environment")
	tree = ET.parse(EnvironmentFile)
	root = tree.getroot()

	# 尋找 type 節點
	for _type in root.iter('type'):
	    _type.text = typeName

	# 寫入 XML 檔案
	# 引數1：xml檔案生成的位置和名字，引數2：指定xml編碼，引數3：xml 宣言，
    # xml 宣言即：是否有 <?xml version='1.0' encoding='utf-8'?> 在開頭 (不確定是否必要)
	tree.write(EnvironmentFile, encoding="utf-8", xml_declaration=True)

# 更動 PatchSetting.json
def EditPatchSettingJson(data:dict):
	print("\tEdit PatchSetting.json with", data)
	patchContent = {}
	# 讀取 PatchSetting.json
	file = open(PatchSettingFile,"r")
	patchContent = json.load(file)

	# 更改 PatchSetting.json 內的值
	for key, value in data.items():
		print("\t",key, ":",patchContent[key], '->', value)
		if patchContent[key]:
			patchContent[key] = value

	file.close()

	# 寫入 PatchSetting.json
	with open(PatchSettingFile,"w") as file:
	    json.dump(patchContent, file, indent=2) 	

# 更改環境時用
def ChangeEnvironment(typeName:str):
	EditEnvironmentXml(typeName)
	EditPatchSettingJson(EnvironmentPatchSetting[typeName])

# 確定資訊暫停用
def StopCheckInfo():
	if not args.needCheck:
		return
	while(True):
		getInput = input("Continue?(Y/N):")
		if getInput.upper() == "N":
			exit()
		elif getInput.upper() == "Y":
			break
		else: 
			print("Wrong input, try again:\n")

# 判定apk是否build成功
def ChekBuildSuccess(buildInfoStr:str) -> BUILD_CODE:
	if SuccessStr in buildInfoStr.split('\n')[0]:
		print("\tbuild apk finish")
		return BUILD_CODE.SUCCESS
	elif ThreadFailStr in buildInfoStr.split('\n')[0]:
		print("\tFailed because thread problem ")
		return BUILD_CODE.Thread_Failed
	else:
		print("\tFailed by unknown reason (┳Д┳)")
		return BUILD_CODE.Unknown_Failed
#
# 運作流程大致上就是
# 1. 更改目前建置方案需要更動的檔案
# 2. 執行 build apk 的指令
# 3. 成功進下一輪, 如果因為 thread 原因造成失敗當前建置方案再跑一次
#
def main():
	timestart = time.time()
	timeStartStr = time.strftime("%H-%M-%S", time.localtime())
	cmdStr = ""
	BuildCount = 1
	for buildSetting in BuildSetting:
		for envir in EnvironmentSetting:
			# 建置前設定參數
			cmdStr = BuildCmdStr + buildSetting['BuildName']
			buildType = "debug" if "debug" in buildSetting['BuildName'].lower() else "release"
			moveToPath = './AutoOutput'+timeStartStr+'/'+buildSetting['PatchSetting']['REGION_CHANNEL']+"/"+buildSetting['PatchSetting']['MARKETING_CHANNEL']+"/"+envir

			print("No.",BuildCount,":")
			print("\tBuildType:\t", buildType)
			print("\tEnvironment:", envir)
			print("\tMARKETING:\t", buildSetting['PatchSetting']['MARKETING_CHANNEL'])
			print("\tREGION:\t\t", buildSetting['PatchSetting']['REGION_CHANNEL'])
			print("\tCommand:\t", cmdStr)
			print("\tMoveTo:\t", moveToPath)
			
			StopCheckInfo()
			EditPatchSettingJson(buildSetting['PatchSetting'])
			ChangeEnvironment(envir)

			buildFailedCount = 0
			# 執行建置
			while(True):
				buildResult = os.popen("python generateTestFile.py --path="+buildSetting['outputPath'])
				# buildResult = os.popen(cmdStr)
				resultStr = buildResult.read()
				resultCode = ChekBuildSuccess(resultStr)
				if resultCode == BUILD_CODE.SUCCESS:
					break
				elif resultCode == BUILD_CODE.Unknown_Failed:
					exit()
				else:
					buildFailedCount += 1 

			# 將建置完的apk轉移到整理的地方
			isPathExist = os.path.isdir(moveToPath)
			if not isPathExist:
				os.makedirs(moveToPath)

			shutil.move(buildSetting['outputPath'], moveToPath)
			
			# go next
			BuildCount += 1
	timeEnd = time.time()

	print("Finish. It cost "+format_timespan(int(timeEnd - timestart)))
if __name__ == '__main__':
	main()