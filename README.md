
Apriltag :package: 
--------

apriltag marker detection based on <https://github.com/ChahalSandeep/apriltag>

It fixes some of issues caused when you download from pip.


Dependencies
------------

  - OpenCV (optional)
  
Installation and Running  :nut_and_bolt:
------------------------
   1. Clone this repository in your system 
        ```commandline
        git clone https://github.com/ChahalSandeep01/apriltag.git
        ```
   2. Go to cloned folder and run setup.py
        ```commandline
        cd path/to/apriltag
        python setup.py install
        ```
   
   Now you are all set
   
How to use it in your code  :computer:
--------------------------
   ```python
import apriltag # importing

detector = apriltag.Detector() #creating an object of class Detector

result = detector.detect(img)  # calling method detect and it results april tag details

print (result) 
   ```

Results in the form of 

    [DetectionBase(tag_family='tag36h11', tag_id=2, hamming=0, goodness=0.0, decision_margin=98.58241271972656, homography=array([[ -1.41302664e-01,   1.08428082e+00,   1.67512900e+01],
       [ -8.75899366e-01,   1.50245469e-01,   1.70532040e+00],
       [ -4.89183533e-04,   2.12210247e-03,   6.02052342e-02]]), center=array([ 278.23643912,   28.32511859]), corners=array([[ 269.8939209 ,   41.50381088],
       [ 269.57183838,   11.79248142],
       [ 286.1383667 ,   15.84242821],
       [ 286.18066406,   43.48323059]])),
    DetectionBase(tag_family='tag36h11', ... etc

How to use more information from it
-----------------------------------
once you have got it in results you can retrive information like below example
```python
for tags in result:
    print tags.tag_id
    print tags.corners
    print tags.center
    print tags.tag_family
    print tags.decision_margin

```


.