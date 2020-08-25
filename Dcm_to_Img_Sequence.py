# This program is written by Abubakr Shafique (abubakr.shafique@gmail.com) 
import os
import cv2 as cv
import numpy as np
import pydicom as PDCM

def Dicom_to_Image(Path):
    DCM_Img = PDCM.read_file(Path)

    rows = DCM_Img.get(0x00280010).value #Get number of rows from tag (0028, 0010)
    cols = DCM_Img.get(0x00280011).value #Get number of cols from tag (0028, 0011)

    Instance_Number = int(DCM_Img.get(0x00200013).value) #Get actual slice instance number from tag (0020, 0013)

    Window_Center = int(DCM_Img.get(0x00281050).value) #Get window center from tag (0028, 1050)
    Window_Width = int(DCM_Img.get(0x00281051).value) #Get window width from tag (0028, 1051)

    Window_Max = int(Window_Center + Window_Width / 2)
    Window_Min = int(Window_Center - Window_Width / 2)

    if (DCM_Img.get(0x00281052) is None):
        Rescale_Intercept = 0
    else:
        Rescale_Intercept = int(DCM_Img.get(0x00281052).value)

    if (DCM_Img.get(0x00281053) is None):
        Rescale_Slope = 1
    else:
        Rescale_Slope = int(DCM_Img.get(0x00281053).value)

    New_Img = np.zeros((rows, cols), np.uint8)
    Pixels = DCM_Img.pixel_array

    for i in range(0, rows):
        for j in range(0, cols):
            Pix_Val = Pixels[i][j]
            Rescale_Pix_Val = Pix_Val * Rescale_Slope + Rescale_Intercept

            if (Rescale_Pix_Val > Window_Max): #if intensity is greater than max window
                New_Img[i][j] = 255
            elif (Rescale_Pix_Val < Window_Min): #if intensity is less than min window
                New_Img[i][j] = 0
            else:
                New_Img[i][j] = int(((Rescale_Pix_Val - Window_Min) / (Window_Max - Window_Min)) * 255) #Normalize the intensities

    return New_Img, Instance_Number

def main():
    Input_Folder = 'Sequence_Data'
    Output_Folder = 'Sequence_Output'

    Input_Image_List = os.listdir(Input_Folder)

    if os.path.isdir(Output_Folder) is False:
        os.mkdir(Output_Folder)
    
    for i in range(0, len(Input_Image_List)):

        Output_Image, Instance_Number = Dicom_to_Image(Input_Folder + '/' + Input_Image_List[i])

        cv.imwrite(Output_Folder + '/' + str(Instance_Number - 1).zfill(4) + '.jpg', Output_Image)

if __name__ == "__main__":
    main()