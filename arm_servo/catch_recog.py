imoprt cv2

# Determine modules are at the top of the screen
top_value = 50

def catch_recog(img):
	"""
	Determine modules are at the top of the screen
	arg:
		img
	return:
		bool 
	"""
	
	m = cv2.moments(img,False)
	x,y = m["m10"]/m["m00"],m["m01"]/m["m00"] 
	catch = False
	if y < 50:
		print("the module is at the top of the screen")
		catch = True
	else:
		catch = False
		
	return catch
