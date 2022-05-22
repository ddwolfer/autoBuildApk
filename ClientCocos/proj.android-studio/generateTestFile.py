import argparse
import os
import time
import random

parser = argparse.ArgumentParser(description='')

parser.add_argument('--path', dest='path', type = str, default='./', help='path of output file')
parser.add_argument('--fileName', dest='fileName', type = str, default='temp.txt', help='output file name')

args = parser.parse_args()

def main():
	time.sleep(1)

	testRes = random.randint(1,1)
	if testRes == 1:
		isExist = os.path.isdir(args.path)
		if not isExist:
			os.makedirs(args.path)

		with(open(os.path.join(args.path, args.fileName), 'w')) as file:
			file.write("test")

		print("BUILD SCCESSFUL\n ")
	else:
		print("thread failed\n ")

if __name__ == '__main__':
	main()