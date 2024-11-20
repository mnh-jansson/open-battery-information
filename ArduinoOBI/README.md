# ArduinoOBI

## Hardware

This simple interface can be built using an Ardunio Uno and some external resistors. 

![screenshot](../docs/images/arduino-obi.png)

---

## Prerequisites

Ensure you have the following installed on your system:

1. **VS Code (Visual Studio Code)**  
   Download from [here](https://code.visualstudio.com/).

2. **PlatformIO Extension for VS Code**  
   Install the PlatformIO extension from the Extensions Marketplace in VS Code.

3. **Git (OPTIONAL)**  

4. **Arduino UNO**  
   Ensure you have a working Arduino UNO board and a USB cable to connect it to your computer.
   Build the circuit according to the schematic.

---

## Step 1: Clone the ArduinoOBI Repository

1. Open your terminal.
2. Clone the repository using the command:

   ```bash
   git clone https://github.com/mnh-jansson/open-battery-information.git
   ```

Or,

1. Download the repository as a .ZIP file.
---

## Step 2: Open the Project in VS Code

  Open VS Code.
  Go to File > Open Folder and select the ArduinoOBI project folder.
  PlatformIO will automatically detect the project. If not, ensure the folder contains a platformio.ini file.

## Step 3: Compile the Project

  Open the PlatformIO sidebar by clicking on the PlatformIO icon in the VS Code activity bar.
  Click on the "Project Tasks" dropdown for uno.
  Under "General", click Build to compile the code.
  Check the output terminal for any errors. A successful build will show a "Success" message.

## Step 4: Flash the Code to the Arduino UNO

  Connect your Arduino UNO to your computer using a USB cable.
  In the PlatformIO sidebar, go to the "Project Tasks" dropdown for uno.
  Under "General", click Upload.
  PlatformIO will detect the correct port and upload the firmware to your Arduino UNO.
  A successful upload will display an "Upload complete" message in the terminal.
