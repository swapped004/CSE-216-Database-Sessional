#
# Save on a new file with the same name but with "small_" prefix
# on high quality jpeg format.
#
# If the script is in /images/ and the files are in /images/2012-1-1-pics
# call with: python resize.py 2012-1-1-pics

from PIL import Image
import os
import sys

directory = 'E:\\NETFLIX\\static\\home\\shows\\css\\images\\'
for file_name in os.listdir(directory):
	if file_name.endswith(".jpg") or file_name.endswith(".png"):
		print("Processing %s" % file_name)
		image = Image.open(os.path.join(directory, file_name))

		x,y = image.size
		new_dimensions = (1800, 2666) #dimension set here
		output = image.resize(new_dimensions, Image.ANTIALIAS)

		output_file_name = os.path.join(directory,file_name)
		output.save(output_file_name, "JPEG", quality = 95)

print("All done")