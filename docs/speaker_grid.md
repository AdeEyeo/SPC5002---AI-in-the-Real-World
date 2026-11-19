# Speaker grid

Every guest on the module is asked the same six questions, and the seventh is
for you alone. There are four guests this term, in Weeks 3, 6, 9 and 12, and in
the spring you choose a project partly from what is written here.

Write each answer in your own words while it is fresh, the same day.

## Week 3, Friday 9 October

Speaker: Shiyamalaraj Kandasamy - PhD Candidate, Lecturer in Computing
Organisation: School of Computing, University of Buckingham (research in partnership with Flintec, a load cell manufacturer)

1. What is your field?

Quality engineering in high-precision manufacturing, statistical process control, data science, machine learning, process mining

2. How do you use machine learning?

Defect prediction (pass/fail classification), quality prediction, anomaly detection (process drift), root cause analysis, clustering (rerun vs rework), process mining, sequence mining

Defect prediction and clustering are the parts he has actually done. Quality prediction, anomaly detection and root cause analysis are the opportunities he is targeting, and sequence mining is in progress.

3. What data do you use, and how do you clean it?

15 years of Flintec production data, including:
- Machine shop: serial number, material properties, machines used, operators, outcome (pass/fail)
- Production records: job cards, shifts, machine breakdowns and services
- Operator-logged events (tool breaks, alarms, end of shift) alongside inspection measurements
- Timestamped test records for each stage (serial number, timestamp, stage)

Rejects weren't recorded, so he inferred them by comparing generated serial numbers with scanned ones. Missing machine and operator data for rejected parts was filled in from the rest of the batch (an assumption). Because job cards link to many shifts, he could only match groups of machines to groups of serial numbers.

For the journey data, he standardised date formats and merged "sibling" tables, where old and new systems recorded the same visit seconds apart. He checked with IT teams about tables that overwrite old records. Process mining derived the intended path for each part number, and each serial number got a fitness score (0-1) for how far it deviated, which is used to filter out good product. Each journey was turned into a sequence of ordered stage codes, and each transition was labelled as expected, upstream rework or same-stage rerun.

To separate rerun from rework: a part repeated straight away at the same workstation is a rerun. Otherwise, the time between repeats at each workstation is clustered into two groups (k = 2) and the midpoint is used as a threshold, with a minimum number of data points required. Reruns are removed and only the latest result is kept.

4. What does your pipeline look like?

Factory: Procurement -> Machine shop -> QA -> Heat treatment -> Surface treatment -> Strain gauge manufacturing -> Gaging -> Assembly

One product's journey: SG application -> Wiring -> Pre-stress -> TCZero -> Calibration (with rework loops back to the same or earlier stages, or scrap)

Data pipeline: Raw database tables -> Pre-processing -> Process mining (intended path) -> Fitness score -> Sequence extraction -> Transition labelling -> Rerun/rework clustering -> Sequence mining -> Classification and root cause analysis (planned) -> Findings documented in Flintec's ISO 9001 system

5. How do you check your results, and change what you do?

Machine shop classifiers were measured with accuracy, true positive rate, true negative rate and F1 score. Accuracy was 0.98, but the true positive rate was only 0.05-0.25 (Bayesian reached 0.40 but with 0.63 accuracy), and SMOTE didn't help. He found a 2% reject rate and no features separating passes from fails: distance to the 25th nearest neighbour was about 0, and isolated points didn't have higher reject rates. He dropped this experiment and designed new ones.

He plotted a dimension against operator-logged events, the nominal value and the specification limits. There were abnormal shifts after tool changes and an alarm, but the dataset is too small, so more data is being collected before he advises the company.

Factory staff told him that not every repeat is a rework, which led him to add the rerun/rework step. He validated the process-mined intended paths against Flintec's documentation. The fitness score histogram showed about 49% of parts close to 1, and he has since improved the pipeline. Sequence mining results are judged by support and confidence; early results are probably wrong and are being redone on the cleaned sequences. He uses generative AI only to validate his code and checks it line by line before relying on it.

6. Who do you have to explain all this to?

Flintec (management, process and IT teams, process engineers), shop-floor staff and quality engineers who would need to trust and use the models, the research community (publishing needs proof on general open datasets), his students

7. Could I see myself doing this work, and why?

No. The part that appealed to me most was when he designed a solution after spotting the root issue, such as separating reruns from reworks. I enjoy problem-solving when the problem is well defined, like a maths question, and I like the sense of accomplishment with each step of progress and the excitement of finding a solution. However, much of his work was cleaning data. I believe data is hard to fix because the devices that collect it need to be set up when the factory and its pipeline are first built, so fixing it means making a lot of assumptions based on background knowledge, like filling in missing machine and operator data. As an indecisive and hesitant person, I don't feel comfortable making assumptions when the cost of getting it wrong is this high. I'm mostly fine with slow progress, depending on deadlines, as long as each step is meaningful and helps me plan what to do next. But I prefer technical work and feel uncomfortable talking to unfamiliar people, so having to chase factory teams for data, as he has been doing since April, would put me off. I would rather work on cleaner, more general problems that are easier to solve.

## Week 6

Speaker: Dr Adam Keane - Senior Research Associate
Organisation: The Alan Turing Institute (Project Bluebird, with NATS and the University of Exeter)

1. What is your field?

AI safety and assurance for safety-critical systems, air traffic control (aviation), digital twins, data science

2. How do you use machine learning?

- Probabilistic trajectory generation (functional PCA, Gaussian mixture models)
- Adaptive real-time trajectory prediction (surrogate model)
- AI agents to control aircraft:
  - rules-based (Hawk, Bond)
  - optimisation (Falcon)
  - reinforcement learning (LAgent, d2mav)
- Explainability (Shapley values, sensitivity analysis, surrogate models, counterfactuals)
- Out-of-distribution detection (nearest neighbours, GMM density)
- LLMs to design training scenarios

3. What data do you use, and how do you clean it?

- Radar: position, altitude, speed, heading, squawk code
- Clearances: vertical instructions, vectors, route following, speed control
- Flight data: callsign, aircraft type, filed route, origin and destination
- Airspace configuration: sector shape, bandbox status, waypoints
- Weather forecasts: pressure bands by latitude, longitude and altitude, used to infer wind vectors

Data comes from NATS and the Met Office. A separate team of data wranglers cleans it in multiple steps and makes it uniform; the speaker didn't know the details. Data quality is checked for accuracy, completeness, consistency, validity, uniqueness and timeliness. The checks look for outliers, duplicates, contradictory values, sensor or annotation errors and stale data.

4. What does your pipeline look like?

Real en-route airspace data -> Cleaning and processing -> Digital twin data handler (weather, airspace, procedures, aircraft) + probabilistic trajectory generation -> AI agent via REST API -> Metrics, visualisation and logs -> Human-in-the-loop assessment -> Feedback

Deployment path: Lab (digital twin) -> Performance metrics -> Human-in-the-loop trials -> Operational explainability -> Digital twin validation -> Assurance case and ODD -> Regulator

5. How do you check your results, and change what you do?

- Performance metrics:
  - minimum separation of 5 NM laterally and 1,000 ft vertically, safe over a 10–20 minute horizon
  - sector discipline
  - being expeditious; unnecessary clearances count as faults
- Human-in-the-loop trials:
  - agents sit an adapted version of the 5-month controller basic training course (Medway sector, 39 objectives)
  - 3 held-back exams are marked by controllers on a 4-point scale, then moderated
  - Hawk failed rounds 1 and 2, was updated after controllers' feedback, and passed round 3; safety was the hardest competency
- Digital twin validation:
  - predicted and real distributions are compared with Wasserstein distance, KS statistic, KL divergence and QQ plots
  - the failure target is <1×10⁻⁹ to 1×10⁻³ per flight hour, depending on use
  - a live shadow trial was run
- Operational design domain: flags out-of-distribution situations at runtime, such as storms or emergency aircraft.
- Assurance case: property claims are selected from EASA's objectives for the system's level of AI autonomy, and each claim is backed by evidence.

6. Who do you have to explain all this to?

Air traffic controllers (users and assessors), NATS, regulators (EASA), government, the public, other researchers and model developers

7. Could I see myself doing this work, and why?

I'm not sure. The part I found most interesting was building the AI agents, but I would need to learn all of the skills involved thoroughly. The speaker stressed that domain knowledge matters most. I'm fine with a subject close to computer science, like maths, but I would prefer to work in my own field of study rather than air traffic control. The pace also matters: the project is still far from deployment after a year and a half, so it could easily need another 18 months. I'd accept that if I were paid and could see progress, but not as an unpaid personal project unless it ran alongside a job. Most of all, I would be very uncomfortable with the responsibility, since failures in this system could cost lives. I would step back from it unless I was the only one who could do it.

## Week 9

Speaker and organisation

1. What is your field?
2. How do you use machine learning?
3. What data do you use, and how do you clean it?
4. What does your pipeline look like?
5. How do you check your results, and change what you do?
6. Who do you have to explain all this to?
7. Could I see myself doing this work, and why?

## Week 12

Speaker and organisation

1. What is your field?
2. How do you use machine learning?
3. What data do you use, and how do you clean it?
4. What does your pipeline look like?
5. How do you check your results, and change what you do?
6. Who do you have to explain all this to?
7. Could I see myself doing this work, and why?
