# ANISMA Software
ANISMA Software is a software to design and test ANISMA Skin Deformation devices to provide haptic stimuli like pressure, stretch and motion on the skin.
ANISMA Skin Deformation devices use Shape-Memory Alloys (SMAs) which contract like an artificial muscles when power is applied.
Using ANISMA Software, devices can be designed and tested virtually. It is also suitable to learn the characteristics of SMAs. 

In addition, ANISMA Software allows exporting the design and helps programming and actuating ANISMA devices that were created with the help of the ANISMA hardware kit. If you do not have the hardware kit available, ANISMA software may still help you derive the design parameters for your implementation of SMAs.

<img src="https://user-images.githubusercontent.com/62531877/225146327-58325651-7271-4761-96e6-4343f5e53d2e.png" width="80%" height="80%">


## How to run ANISMA software

1. Download or clone the repository
```
git clone https://github.com/augmented-human-lab/ANISMA-software.git
```

2. Navigate into the ANISMA-software directory and set up a new virtual environment
```
cd ANISMA-software/
virtualenv env
source env/bin/activate
```

3. Install the anisma dependencies using the python package manager inside the virtual environment
```
pip install -r requirements.txt
```

4. Run ANISMA software using python3
```
python3 ./anisma-software/main.py
```

5. You can now start designing anisma devices and test and preview their behaviour.
If you have the hardware kit available you can connect the Arduino Controller Board, connect the ANISMA device to the Driver Board as indicated, and start the physical actuation from the Animate tab.

