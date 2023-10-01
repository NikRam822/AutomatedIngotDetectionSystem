# Client's Interview Notes
### Conducted on September 28, 2023

1. The company makes aluminum ingots and sell it to other factories and companies.
2. The analysis for defects is currently made by human engineers, and its ineffective.
3. Some examples of good and bad ingots were shown by the client.
	1. Humans are not accurate and tend to make false positives.
4. We do not need to do ML on images, just data collection board.
5. The camera is already installed in the certain place, where it could see ingot.
6. It is only one camera for the first stage, but there five more will be installed later to take pictures from different views. All cameras will be placed on sides, it is impossible to set the camera on the ceiling due to building architectural limitations.
7. There are some challenges need to be solved:
	1. The camera is not placed at a straight angle, so image proportions should be adjusted, because images from the learning dataset has been taken under the direct angle.
	2. When it's sunny outside (in the morning), the aluminum catches sun and shines, so we need to adjust camera's settings (exposure) to reduce brightness of the image. In the evening and night we need to change it back.
	3. The camera is placed very far from the line so it should not suffer from the high temperature, but it may affect the picture's quality. Although the camera is 4K and ML needs only 500x500 image.
8. There are two types of defects that should be addressed by the system:
	1. The aluminum dross – oxygen bubbles on the surface produce aluminum oxide.
	2. The aluminum discoloration – the ingot may be of yellow color after cooldown. It is not very common and there are not many samples of this defect.
9. There may be another defects like holes, cracks, but for now we should not detect them.
10. Defected ingots are going to the recycle.
11. There's a video of the full production process, that will be provided later after the interview.
12. The solution with the camera provides acceptable level of defect detection so the client do not consider alternative technical solutions at the moment.
13. The proposed technical solution:
	1. The camera will be connected to the laptop, and our software should run on the laptop.
	2. The factory automation system detects the next aluminum tray and send us a signal, that we could start the analysis. Each aluminum ingot has its own ID so it could be easily identified.
	3. We need to collect data from the camera to teach an ML model.
		1. The image should be cropped to remove surroundings of the ingot.
		2. The cropped region should be transformed to adjust the viewport to the straight angle.
		3. The worker will analyze the result and mark the image if it's OK or not.
	4. After initial data collection and markup, we need to train the model.
	5. The trained model will operate under human control for some time and continue it's learning. When the accuracy of prediction become stable, it will be running autonomously.
	6. We do not need to create and train model, it's a Yusuf's people part of the job. We only need to provide a system to collect and organize data.
	7. The backend part should be integrated with ML engine written with Python, so it's suggested to use Python for the backend. But we are free to propose a different solution.
		1. Proposed solution should be maintainable, as Yusuf's people may want to change something on the backend or frontend parts of the system, so it's better to not use arcane technologies.
	8. To address the light issue, we need to correct the camera's exposure time. We need to find a solution to do it automatically.
	9. The user of the system is not technician, it's a factory worker with basic PC operation skills. So the UI should be as simple as possible.
14. The actors:
	1. Yusuf's developers who will set the system up and support it in the field.
	2. Factory workers who will collect, mark and verify data manually.
15. They tried the similar system from the another vendor, but the solution was not able to manage a sunshine issue.
16. There are no particular constraints on budget, but all additional spendings should be justified.
17. The desired time for the regular weekly meetings:
	1. Monday evening
	2. Wednesday evening
18. We decided to create a group in TG to discuss further questions online.