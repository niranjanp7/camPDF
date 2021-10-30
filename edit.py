import cv2
import numpy


def show(imgArray,scale=0.5,lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = numpy.zeros((height, width, 3), numpy.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = numpy.hstack(imgArray[x])
            hor_con[x] = numpy.concatenate(imgArray[x])
        ver = numpy.vstack(hor)
        ver_con = numpy.concatenate(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= numpy.hstack(imgArray)
        hor_con= numpy.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth= int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        print(eachImgHeight)
        for d in range(0, rows):
            for c in range (0,cols):
                cv2.rectangle(ver,(c*eachImgWidth,eachImgHeight*d),(c*eachImgWidth+len(lables[d])*13+27,30+eachImgHeight*d),(255,255,255),cv2.FILLED)
                cv2.putText(ver,lables[d],(eachImgWidth*c+10,eachImgHeight*d+20),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),2)
    cv2.imshow("Result", ver)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


class MyImage:
    def __init__(self, img_path):
        self.image = cv2.imread(img_path)

    def extract_image(self):
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blur_image = cv2.GaussianBlur(gray_image, (5, 5), 1)
        dimention = self.image.shape
        toatal_area = dimention[0]*dimention[1]
        for th1 in range(120,20,-1):
            threshold = (th1, 80)
            thrs_image = cv2.Canny(blur_image, threshold[0], threshold[1])
            base = numpy.ones((5, 5))
            dial_image = cv2.dilate(thrs_image, base, iterations=2)
            thrs_image2 = cv2.erode(dial_image, base, iterations=1)
            contours, hierarchy = cv2.findContours(thrs_image2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cont_image = self.image.copy()
            cv2.drawContours(cont_image, contours, -1, (0, 0, 255), 5)
            largest, area = self.huge_area(contours)
            document = self.image.copy()
            if largest.size !=0:
                largest = self.shape(largest)
                cv2.drawContours(document, largest, -1, (0, 0, 255), 10)
                cv2.line(document, (largest[0][0][0], largest[0][0][1]), (largest[1][0][0], largest[1][0][1]), (0, 255, 0), 2)
                cv2.line(document, (largest[0][0][0], largest[0][0][1]), (largest[2][0][0], largest[2][0][1]), (0, 255, 0), 2)
                cv2.line(document, (largest[3][0][0], largest[3][0][1]), (largest[2][0][0], largest[2][0][1]), (0, 255, 0), 2)
                cv2.line(document, (largest[3][0][0], largest[3][0][1]), (largest[1][0][0], largest[1][0][1]), (0, 255, 0), 2)
                width, height = self.dimention(largest)
                corners = numpy.float32(largest)
                dimentions = numpy.float32([[0, 0], [width, 0], [0, height], [width, height]])
                grid = cv2.getPerspectiveTransform(corners, dimentions)
                wrap_image = cv2.warpPerspective(self.image, grid, (width, height))
            if area>(0.4*toatal_area):
                show([[gray_image, blur_image, thrs_image], [dial_image, thrs_image2, cont_image]])
                cv2.imshow("Image", wrap_image)
                cv2.waitKey(0)
                return wrap_image
        #show([[gray_image, blur_image, thrs_image], [dial_image, thrs_image2, cont_image]])
        #cv2.imshow("Image", wrap_image)
        #cv2.waitKey(0)
        return self.image

    def huge_area(self, contours):
        largest = numpy.array([])
        area = 0
        for i in contours:
            sample = cv2.contourArea(i)
            perimeter = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * perimeter, True)
            if sample>area and len(approx) == 4:
                largest = approx
                area = sample
        return largest, area

    def shape(self, largest):
        largest = largest.reshape((4, 2))
        ordered = numpy.zeros((4, 1, 2), dtype=numpy.int32)
        ordered[0] = largest[numpy.argmin(largest.sum(1))]
        ordered[1] = largest[numpy.argmin(numpy.diff(largest, axis = 1))]
        ordered[2] = largest[numpy.argmax(numpy.diff(largest, axis = 1))]
        ordered[3] = largest[numpy.argmax(largest.sum(1))]
        return ordered

    def dimention(self, box):
        (([a], [b], [c], [d])) = box
        width_top = int(numpy.sqrt(pow(a[0]-b[0], 2) + pow(a[1]-b[1], 2)))
        width_bottom = int(numpy.sqrt(pow(c[0]-d[0], 2) + pow(c[1]-d[1], 2)))
        height_left = int(numpy.sqrt(pow(a[0]-d[0], 2) + pow(a[1]-d[1], 2)))
        height_right = int(numpy.sqrt(pow(b[0]-c[0], 2) + pow(b[1]-c[1], 2)))
        return max(width_top, width_bottom), max(height_left, height_right)


if __name__ == "__main__":
    img = MyImage("D:\\Image\\3.jpg")
    img.extract_image()
