# 🥗 SmartPlate

### Smarter portions. Less food waste.

**SmartPlate** is a student-built, Python-based web application prototype designed around food-waste awareness at **FIU's 8th Street Campus Kitchen**. It helps students consider portion sizes before ordering, record leftovers after eating, and earn points for waste-conscious habits. The resulting feedback can support data-driven conversations about dining operations.

> **Project status:** Hackathon prototype. SmartPlate is **not** an official FIU Dining service, does not process real dining orders, and has not yet demonstrated a measured reduction in food waste.

## 🌎 The problem and our approach

Food waste can mean wasted food, water, energy, and money. Students may take more food than they finish, while dining managers may have limited insight into which menu items are frequently left over.

SmartPlate explores a **prevent → track → learn** approach:

1. **Prevent:** Suggest meal combinations and display non-blocking portion reminders before ordering.
2. **Track:** Ask students to report how much food remains after a meal and identify leftover items.
3. **Learn:** Store structured feedback that can be analyzed for recurring waste patterns.

The project aligns with **UN Sustainable Development Goal 12: Responsible Consumption and Production**.

## ✨ Key features

- **Demo student login:** Name and seven-digit Panther ID format validation (not official FIU authentication).
- **Hunger-based suggestions:** Rule-based meal combinations using menu items and a selected hunger level: *Light*, *Moderate*, or *Very Hungry*.
- **Menu browsing and custom orders:** Browse items by food station or build a personalized plate with a running estimated calorie total.
- **Portion reminders:** Non-blocking prompts when a custom order exceeds a configurable prototype threshold; students remain free to continue.
- **Digital order ticket:** A simulated station-by-station workflow for *Preparing*, *Ready*, and *Collected* statuses.
- **Post-meal feedback:** After a short demo countdown, students report leftovers and may specify which foods remained. Unfinished feedback can be restored after returning to the app.
- **SmartPoints:** A proposed reward mechanism tied to reported leftover levels.
- **Personal impact view:** Summary of recorded meals, reported waste patterns, and accumulated points.
- **Analytics-ready records:** CSV outputs that can be explored in Power BI for food, station, and feedback trends.

## 🔄 How it works

```text
Demo login
    ↓
Choose hunger level
    ↓
Suggestions / Browse menu / Build an order
    ↓
Portion reminder (when applicable)
    ↓
Review order → Simulated station pickup
    ↓
Demo countdown → Leftover feedback
    ↓
SmartPoints + personal impact
    ↓
CSV data for further analysis
```

## ⭐ SmartPoints (prototype)

| Reported leftovers | Points earned |
| --- | ---: |
| Nothing | 20 |
| A little | 10 |
| Some | 5 |
| A lot | 0 |

The proposed reward is **1,000 points for one free meal**. This is a design concept, **not an existing FIU Dining benefit**. Points are based on **self-reported feedback**, not verified food-waste measurements.

## Tech stack

| Technology | Purpose |
| --- | --- |
| Python | Application logic and data processing |
| Streamlit | Interactive web interface |
| Selenium | Browser automation for menu collection |
| Pandas | Data analysis and visualization support |
| CSV | Prototype storage for menus, profiles, orders, and feedback |
| Power BI | Team's downstream analytics and dashboard workflow |

**Recommendation transparency:** The current recommendation engine is **rule-based**, not a trained AI or machine-learning model.

## Project structure

| File | Role |
| --- | --- |
| `streamlit_app.py` | Main student-facing Streamlit application |
| `recommendation.py` | Hunger-based meal suggestion logic |
| `menu_scraper.py` | Menu collection using Selenium |
| `current_menu.csv` | Menu data used by the application |
| `meal_history_demo.csv` | Example/demo meal-history data |
| `student_profiles_demo.csv` | Example/demo student-profile data |
| `meal_history.csv` | Local meal and feedback records |
| `student_profiles.csv` | Local prototype student profiles |
| `pending_orders.csv` | Local orders awaiting feedback |

Other files in the repository may be supporting or experimental assets.

## Run locally

**Prerequisites:** Python 3.10+ and a terminal. Running the menu scraper additionally requires Google Chrome and a compatible Selenium browser driver setup.

1. Clone the repository and enter the project folder:

   ```bash
   git clone https://github.com/tuyennguyen16/SmartPlate.git
   cd SmartPlate
   ```

2. (Recommended) Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the Python dependencies:

   ```bash
   pip install streamlit pandas selenium
   ```

4. Run the application:

   ```bash
   streamlit run streamlit_app.py
   ```

5. Open the local URL printed in the terminal. The application reads `current_menu.csv` if available. To attempt a fresh menu collection, run `python3 menu_scraper.py` separately, then restart or reload the app as needed.

**Demo note:** Use fictional student names and seven-digit IDs. This prototype uses local CSV files and is not suitable for handling real student data without additional security and privacy controls.

## Sustainability value and evaluation

SmartPlate is intended to support three dimensions of sustainability:

- **Environmental:** Encourage more thoughtful portions and potentially reduce discarded food and the resources embodied in it.
- **Economic:** Provide data that may help dining teams investigate frequently wasted items and improve planning.
- **Social:** Promote awareness and participation through accessible prompts, feedback, and incentives.

These are **potential benefits**, not validated outcomes. A future pilot would compare measured waste and user behavior before and after adoption.

## ## Future Development

Our long-term vision is to transform SmartPlate from a working prototype into a scalable, intelligent, and data-driven solution that supports sustainable dining experiences.

### 1. Machine Learning for Personalized Portion Recommendations

We plan to integrate machine learning to better understand individual students' eating habits and recommend more suitable portion sizes.

By analyzing previous orders, hunger levels, food preferences, and leftover feedback, SmartPlate could identify consumption patterns and continuously improve its recommendations.

For example, if a student frequently leaves rice unfinished, the system could suggest a smaller rice portion in future meals while allowing the student to adjust it according to their needs.

**Goal:** Provide personalized recommendations that improve the dining experience while reducing unnecessary food waste.

### 2. Scalability and System Performance

Our current prototype is built with Python and Streamlit, using CSV files for data storage. To support a larger number of users, we plan to develop a more robust system architecture.

Future improvements may include:

- Migrating from CSV files to a secure, centralized database.
- Developing a more scalable backend and cloud-based infrastructure.
- Improving system performance during peak dining hours.
- Conducting load testing to evaluate reliability with thousands of simultaneous users.

**Goal:** Build a reliable application that can support large university dining communities.

### 3. AI-Powered Leftover Detection and Verification

Currently, SmartPlate relies on students' self-reported feedback to track food waste. In the future, we aim to explore computer vision technology to estimate leftover food from images.

However, image recognition alone cannot guarantee accurate reporting because students could submit misleading photos, such as pictures of empty plates.

To address this challenge, we would explore additional verification methods, including linking feedback to individual orders and testing supervised tray-return stations.

**Goal:** Improve the accuracy and reliability of food waste data while maintaining a convenient user experience.

### 4. Integration with University Dining Services

We hope to collaborate with university dining services to explore integrating SmartPlate into existing dining operations.

Potential developments include:

- Synchronizing menu availability and nutritional information.
- Connecting digital orders with participating food stations.
- Developing a mobile-friendly application for easier student access.
- Providing dining managers with actionable insights through data analytics dashboards.

**Goal:** Connect students' daily dining decisions with more efficient dining operations.

### 5. Measuring Sustainability Impact

To evaluate SmartPlate's effectiveness, we plan to conduct pilot studies with students and university dining services.

These studies could compare food waste before and after implementing SmartPlate, measure student engagement, and identify frequently wasted food items.

The results would help us improve the system and evaluate its potential contribution to **UN Sustainable Development Goal 12: Responsible Consumption and Production**.

**Goal:** Move beyond encouraging sustainable behavior toward measuring meaningful, evidence-based environmental impact.

---

**Our Vision:** SmartPlate aims to create a continuous learning cycle in which student feedback improves portion recommendations, dining data supports better operational decisions, and technology encourages more responsible food consumption.

## Current limitations

- No official FIU login, payment, ordering, or dining-system integration.
- Portion and calorie thresholds are **demo heuristics**, not medical or nutritional advice.
- Leftover reports can be inaccurate or intentionally misreported.
- The station workflow and short feedback timer are simulations.
- CSV storage has limitations for security, reliability, and concurrent usage.
- Real-world food-waste reduction has not yet been established.

## Team and project context

Developed as a student team project for an **AIS Tech X Challenge finalist presentation**. The prototype combines Python application development with a data-analytics workflow to explore more responsible campus dining.

---

*SmartPlate is an independent student prototype. References to FIU and 8th Street Campus Kitchen describe the proposed use case and do not imply official affiliation or endorsement.*
