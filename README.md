Made for physics classes using plotly and dash.

# How to run locally:
1. Clone project.
2. Open terminal and go to ```./web_app``` folder.
3. Install requirements.txt: ```pip install requirements.txt ```.
4. Run project using ```py fizyka_web.py ```.

# How to use:
1. Set how many vector equations You want to show.
2. Set last ```t``` value to calculate (x and y axis boundaries will also be calculated based on that. **Note that in animation, x axis will always start at 0**).
3. Set frequency of calculated points.
4. Set duration of each frame.
5. Set values of each vector equation, where A is x axis, B is y axis. **Only allowed variable is "t". Use python syntax for equations.**
    + Example:
    + A: ```t```
    + B: ```5 * t - (1/2) * 9.81 * t**2```
# Live preview can be seen at: https://fizykawebapp.vercel.app/
