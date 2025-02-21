# inclinometers -- system still in progress
Inclinometer / accelerometer system for measuring inclination angle and tuning motors. Please use file 'UDPsocket_inclinometer.py' as this is the script that will automatically name files. If it does not run properly, resort to 'Backup_UDPsocket.py', which is the original (tested) version.

![Deep Learning-11 2](https://github.com/user-attachments/assets/25a91a8b-a0da-4dc1-b8b6-8d3bf5477a1d)
* NOTE: The 'x', 'y', and 'z' labels on the diagram do not correspond to the correct input channels anymore, due to rewiring that was done. Please do a quick run and just turn them around before use to make sure you know which channel is x/y/z for each accelerometer

<img width="1042" alt="Screenshot 2025-02-20 at 7 04 00 PM" src="https://github.com/user-attachments/assets/750f7eca-c2e5-4107-b66d-b463f6aec26a" />
<img width="1026" alt="Screenshot 2025-02-20 at 7 00 35 PM" src="https://github.com/user-attachments/assets/2968d4f2-d47d-4d62-8944-273dad38e4e5" />
For reference, this is a fourier analysis of the two accelerometers sitting on the quiet table in room 206 inside the box. 

- the 16hz line is caused by the fibre-media converter

- the 0.5hz line and its odd harmonics are caused by ??? idk bro ???

- the 'outside' accelerometer (one with a longer wire) was observed to have some strange spurious signals (mainly observed in its x and z channels), in the range of >20Hz. You can see this a bit in the figure above in channels 2 and 3. Keep an eye on that one! :)
