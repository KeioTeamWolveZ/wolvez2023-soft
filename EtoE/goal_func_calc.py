import numpy as np

def arm_orbit(xz1,xz2,y1,y2):
        a = (xz1-xz2)/(y1-y2)
        b = y1 - a*xz1
        return [a,b]

# normal_x = 0.0281608
# normal_y = 0.00324128
# normal_z = 0.1440181
# high_x = 0.0181661
# high_y = -0.01552108
# high_z = 0.138375
# low_x = 0.0488257
# low_y = 0.0263349
# low_z = 0.141678

normal_x =  -3.76501019e-05
normal_y = 2.52990947e-03
normal_z = -9.27936187e-03
high_x = -0.01691964
high_y = 0.02753068
high_z = -0.00713434
low_x = 0.02653252
low_y = -0.03316158
low_z = 0.00928723

# red module
normal_x = 0.00114863
normal_y = -0.00740776
normal_z = 0.00356848
high_x = -0.00312863
high_y = 0.01556493
high_z = -0.00458264
low_x = 0.01931405
low_y = -0.0416324
low_z = 0.00485871

a_high_x = arm_orbit(high_x,normal_x,high_y,normal_y)[0]
b_high_x = arm_orbit(high_x,normal_x,high_y,normal_y)[1]
a_high_z = arm_orbit(high_z,normal_z,high_y,normal_y)[0]
b_high_z = arm_orbit(high_z,normal_z,high_y,normal_y)[1]
a_low_x = arm_orbit(low_x,normal_x,low_y,normal_y)[0]
b_low_x = arm_orbit(low_x,normal_x,low_y,normal_y)[1]
a_low_z = arm_orbit(low_z,normal_z,low_y,normal_y)[0]
b_low_z = arm_orbit(low_z,normal_z,low_y,normal_y)[1]

print(a_high_x)
print(b_high_x)
print(a_high_z)
print(b_high_z)
print(a_low_x)
print(b_low_x)
print(a_low_z)
print(b_low_z)
