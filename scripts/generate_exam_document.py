from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

OUT = Path(r"D:\Saloni\VU\LY\Adaptive_Healthcare_Project_Exam_Review.docx")

doc = Document()
section = doc.sections[0]
section.top_margin = Inches(0.7)
section.bottom_margin = Inches(0.7)
section.left_margin = Inches(0.75)
section.right_margin = Inches(0.75)

styles = doc.styles
styles['Normal'].font.name = 'Aptos'
styles['Normal'].font.size = Pt(10.5)
styles['Normal'].paragraph_format.space_after = Pt(5)
styles['Normal'].paragraph_format.line_spacing = 1.12
for name, size, color in [('Title', 28, '0F1B33'), ('Heading 1', 18, '0F1B33'), ('Heading 2', 14, '1F4E78'), ('Heading 3', 11.5, '12B5A6')]:
    st = styles[name]
    st.font.name = 'Aptos Display' if name != 'Heading 3' else 'Aptos'
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor.from_string(color)


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), fill)
    tc_pr.append(shd)


def set_cell_text(cell, text, bold=False, color=None):
    cell.text = ''
    p = cell.paragraphs[0]
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(9)
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_heading(text, level=1):
    doc.add_heading(text, level=level)


def add_p(text='', bold_start=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    if bold_start and text.startswith(bold_start):
        p.add_run(bold_start).bold = True
        p.add_run(text[len(bold_start):])
    else:
        p.add_run(text)
    return p


def add_bullets(items, level=0):
    for item in items:
        p = doc.add_paragraph(style='List Bullet' if level == 0 else 'List Bullet 2')
        p.add_run(item)


def add_numbered(items):
    for item in items:
        p = doc.add_paragraph(style='List Number')
        p.add_run(item)


def add_table(headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_text(hdr[i], h, bold=True, color='FFFFFF')
        shade(hdr[i], '1F4E78')
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], str(value))
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_code(code):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    r = p.add_run(code)
    r.font.name = 'Courier New'
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor.from_string('203040')
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(6)


def add_callout(title, text, fill='EEF6FA'):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    cell = table.cell(0, 0)
    shade(cell, fill)
    cell.text = ''
    p = cell.paragraphs[0]
    r = p.add_run(title + ': ')
    r.bold = True
    r.font.color.rgb = RGBColor.from_string('0F1B33')
    p.add_run(text)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

# Cover
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run('ADAPTIVE HEALTHCARE OPERATIONS\nINTELLIGENCE PLATFORM').bold = True
p.runs[0].font.name = 'Aptos Display'
p.runs[0].font.size = Pt(26)
p.runs[0].font.color.rgb = RGBColor.from_string('0F1B33')

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Exam Review, Story Script, Technical Guide and Viva Preparation')
r.font.size = Pt(15)
r.font.color.rgb = RGBColor.from_string('1F4E78')

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run('Project: Adaptive Healthcare Operations Intelligence Platform').italic = True

for _ in range(4):
    doc.add_paragraph()
add_callout('Purpose of this document', 'This guide explains the complete project in simple language, shows how every page works, gives the technical reasoning behind the design, and prepares you for viva or review questions.', 'EAF7F5')
add_p('Prepared from the project README, architecture, assumptions, experiment design, QUBO formulation, source code, API, frontend pages and local test evidence.')

add_heading('How to use this document', 1)
add_bullets([
    'Read Sections 1 to 6 as a continuous presentation story.',
    'Use Sections 7 to 12 for technical questions about code and architecture.',
    'Use Section 15 for a short final exam answer.',
    'Use Section 16 for likely viva questions and suggested answers.',
    'Keep the limitations in Section 17 in mind. Do not claim clinical validity or real quantum advantage.'
])

doc.add_page_break()

add_heading('1. Project in one sentence', 1)
add_p('The project is a local research simulator that compares three hospital resource-allocation approaches - Predictive AI, Quantum-inspired optimization, and a Dynamic Hybrid approach - by running the same synthetic hospital scenarios and measuring unmet demand, capacity, staffing, queues and failures.')
add_callout('Simple definition', 'A hospital simulation plus a comparison platform that helps us ask: under the same workload, which allocation policy handles patients more effectively?', 'EEF6FA')

add_heading('2. The problem it solves', 1)
add_p('Hospitals receive changing numbers of patients. Beds, nurses and department capacity are limited. If patient demand rises faster than available resources, queues grow, waiting time increases and some demand remains unmet.')
add_bullets([
    'Patient arrivals change by time and department.',
    'A bed closure or staffing shortage reduces available capacity.',
    'An admissions surge creates a sudden increase in demand.',
    'Emergency Department overload can affect the full hospital.',
    'Staff must be divided across departments without giving every department an unrealistic advantage.',
    'The result must be measured fairly, not judged by appearance alone.'
])
add_p('The project does not replace a hospital planner or doctor. It is a decision-study and research demonstration using synthetic data.')

add_heading('3. The main story of the project', 1)
add_numbered([
    'Synthetic data creates hourly patient demand for four departments.',
    'The simulation advances one hour at a time.',
    'A forecasting layer estimates future demand for each department.',
    'Three allocation policies interpret the forecast and operational state differently.',
    'The allocation changes beds or nurses in the simulated hospital.',
    'Patients are admitted when capacity exists; otherwise they join the queue.',
    'Temporary disruptions are injected during the run.',
    'The engine records history, unmet demand, utilization and event data.',
    'The dashboard compares policies under identical seed and horizon conditions.',
    'The Failure Lab identifies threshold violations and allows replay of evidence.'
])

add_heading('4. Who uses the system?', 1)
add_table(['User', 'What they can do', 'Why it is useful'], [
    ('Student or researcher', 'Run simulations and experiments', 'Study resource-allocation behavior'),
    ('Project examiner', 'Open dashboards and replay failures', 'Verify that results are visual and reproducible'),
    ('Hospital operations analyst', 'Study beds, nurses and queue effects', 'Explore scenarios before operational planning'),
    ('Administrator', 'Change seed, horizon, mode and disruptions', 'Test different operating conditions'),
])

add_heading('5. The four hospital departments', 1)
add_table(['Department', 'Operational meaning'], [
    ('General Medicine', 'A general ward receiving a broad range of admissions'),
    ('Cardiology', 'A heart-care department with separate beds and queue state'),
    ('Neurology', 'A department handling neurological patients'),
    ('Orthopedics', 'A department handling bone and joint cases'),
])

add_heading('6. Project modules and responsibility', 1)
add_table(['Area', 'Main files', 'Responsibility'], [
    ('Backend simulation', 'backend/simulation/engine.py', 'Clock, arrivals, length of stay, beds, queues and events'),
    ('Forecasting', 'backend/predictive/forecaster.py', 'Per-department model and forecast features'),
    ('Optimization', 'backend/optimization/', 'CP-SAT, QUBO, annealing and Qiskit adapters'),
    ('FastAPI', 'backend/api/routes.py', 'REST API, comparison jobs and stateful demo controls'),
    ('Frontend pages', 'frontend/src/pages/', 'Navigation and each application page'),
    ('Hospital scene', 'frontend/src/game/', 'Visual ward representation'),
    ('Charts', 'frontend/src/charts/', 'Plotly operational analytics'),
    ('Experiment scripts', 'scripts/', 'Data generation, model training and result creation'),
])

add_heading('7. Technology stack', 1)
add_table(['Technology', 'Where it is used', 'Reason'], [
    ('Python', 'Backend and simulation', 'Good for research, forecasting and optimization'),
    ('FastAPI', 'Backend web API', 'Fast REST endpoints and automatic documentation'),
    ('Uvicorn', 'Runs FastAPI server', 'ASGI application server'),
    ('React', 'Frontend user interface', 'Reusable interactive components'),
    ('TypeScript', 'Frontend logic', 'Adds types and catches many mistakes'),
    ('Vite', 'Frontend development server', 'Quick reload and browser serving'),
    ('Zustand', 'Frontend state', 'Stores mode, simulation state and controls'),
    ('Phaser', 'Hospital visual scene', 'Displays the simulated hospital view'),
    ('Plotly', 'Comparison charts', 'Readable interactive charts'),
    ('OR-Tools', 'Hybrid classical solver', 'CP-SAT constraint optimization'),
    ('Ocean and neal', 'Quantum-inspired solver', 'Local simulated annealing for the QUBO'),
    ('Qiskit/Aer', 'Optional QAOA experiment', 'Small local quantum-circuit simulation'),
    ('Docker', 'Container deployment', 'Starts frontend and backend together'),
])

add_heading('8. System architecture', 1)
add_code('React frontend\n  -> REST API calls and polling\n  -> FastAPI routes\n  -> Hospital simulation engine\n  -> Forecasting and allocation policy\n  -> Engine metrics and history\n  -> Zustand, Phaser and Plotly in browser')
add_p('The frontend does not calculate hospital results itself. It sends requests to the backend and displays the returned state. This keeps the simulator and model logic in one place.')

add_heading('9. How the live simulation works', 1)
add_heading('Arrival generation', 2)
add_p('The engine uses a seed to generate repeatable seasonal arrivals. Hour, department, seasonal factors and random noise influence the number of admissions. The seed makes an experiment reproducible: the same seed with the same scenario produces the same starting trajectory.')
add_heading('Length of stay', 2)
add_p('Patients remain in the hospital for a generated length of stay. When a patient leaves, capacity becomes available again.')
add_heading('Queues', 2)
add_p('If no suitable bed is available, patients wait in the queue. This queue becomes a key pressure signal for decision-making.')
add_heading('Disruptions', 2)
add_bullets([
    'Admissions surge: increases patient demand.',
    'Nurse shortage: reduces nurse availability.',
    'Bed closure: removes bed capacity from a department.',
    'ED overload: places additional pressure on emergency and downstream ward operations.'
])
add_heading('Simulation metrics', 2)
add_p('Important metrics include bed utilization, unmet demand, queue size, nurse balance, forecast values and optimizer execution time.')

add_heading('10. The three operating modes', 1)
add_heading('Mode 1: Predictive AI', 2)
add_p('Predictive AI uses expected department demand. Its allocation is based on forecast or recent arrivals. The project uses a greedy forecast allocation: the department that appears to need more staff receives a proportionally larger share of the available pool.')
add_bullets(['Uses demand forecasts', 'Simpler and fast', 'Can react slowly when forecasts are wrong', 'Does not continuously optimize all constraints'])
add_heading('Mode 2: Quantum Optimization', 2)
add_p('Quantum Optimization formulates nurse allocation as a binary optimization problem. The project first builds a QUBO, solves it using local Ocean/neal simulated annealing by default, and can repair invalid allocations to make them feasible.')
add_bullets(['Uses an explicit nurse-allocation objective', 'Quantum-inspired in the normal local comparison', 'Not a real quantum-hardware execution', 'No claim of quantum advantage is made'])
add_heading('Mode 3: Dynamic Hybrid Intelligence', 2)
add_p('Hybrid uses OR-Tools CP-SAT optimization with forecast demand and queue pressure, then replans after every simulation hour and after disruptions. It combines planning with live operational response.')
add_bullets(['Forecast-aware planning', 'Uses queue pressure', 'Applies constraints and objective balancing', 'Replans frequently', 'Better suited to changing hospital conditions'])

add_heading('11. How Predictive AI, Quantum and Hybrid differ', 1)
add_table(['Property', 'Predictive', 'Quantum-inspired', 'Hybrid'], [
    ('Main basis', 'Forecast demand', 'Binary allocation objective', 'Forecast + queue + constraints'),
    ('Decision style', 'Greedy distribution', 'QUBO annealing', 'Constraint optimization and replanning'),
    ('Real-time adaptation', 'Limited', 'Mode result per allocation', 'Every step and after disruptions'),
    ('Best strength', 'Simple forecast response', 'Small binary allocation study', 'Coordinated forecast and live response'),
])

add_heading('12. Forecasting explained simply', 1)
add_p('Forecasting estimates future arrivals before they happen. The project creates features from lag values, rolling averages, calendar information and disruption state. The model is trained per department, or a baseline is used where required.')
add_p('Forecast error is commonly measured with MAPE, or Mean Absolute Percentage Error. A MAPE of 100 percent means the average forecast error is approximately equal to the actual value. MAPE should not be interpreted as a guarantee or as clinical accuracy.')

add_heading('13. The QUBO model', 1)
add_p('A QUBO is a mathematical model containing binary variables and quadratic terms. A binary variable has only two values: 0 or 1. For this project, a variable represents a candidate nurse allocation for a department.')
add_p('For department d and nurse count k, x(d,k) equals 1 if k nurses are assigned to department d. Exactly one option must be selected for every department.')
add_code('sum of x(d,k) for one department = 1')
add_p('The objective prefers nurse allocations close to the forecast workload. Penalties reject allocations that:')
add_bullets([
    'Select more than one nurse option for a department.',
    'Select no nurse option for a department.',
    'Use more nurses than the shared staff budget.'
])
add_p('After the raw binary result is decoded, the system repairs nurse bounds and shared-budget violations. Solver values should be checked after repair, not taken automatically as proof of feasibility.')

add_heading('14. Classical CP-SAT and Hybrid allocation', 1)
add_p('CP-SAT is a constraint programming and integer optimization solver from Google OR-Tools. The Hybrid mode uses constraints so the allocation does not exceed nurse and department limits.')
add_p('It optimizes a staff-allocation objective that considers forecast demand and queue pressure. The exact allocation is recalculated for the current hour. A disruption therefore causes the next allocation to respond instead of continuing with an old decision.')

add_heading('15. Project pages and what to say', 1)
add_heading('15.1 Control Room', 2)
add_p('Purpose: run the live hospital simulation and change it while it is active.')
add_bullets([
    'Run starts the simulation.',
    'Pause stops future hourly progress.',
    'Step advances exactly one hour.',
    'Speed changes how quickly hours advance.',
    'Seed makes stochastic demand reproducible.',
    'Hours sets the horizon.',
    'Apply updates the backend simulation settings.',
    'Mode controls choose Predictive, Quantum or Hybrid.',
    'Disruption buttons inject surge, nurse shortage, bed closure or ED overload.'
])
add_p('The left side shows KPIs and objectives, the center shows the hospital scene, and the right side shows event and department details.')

add_heading('15.2 Arena', 2)
add_p('Purpose: run a matched comparison between all modes.')
add_p('A matched comparison uses the same seed, horizon and scenario. The Arena records bed utilization, unmet demand, nurse balance, optimizer time and final queue size. A background comparison job runs and the frontend polls for the result.')
add_p('Exam explanation: “The Arena is the fairness layer. It ensures that no mode sees a different simulation seed or horizon.”')

add_heading('15.3 Dashboard', 2)
add_p('Purpose: present the latest or recent measured comparison in a readable format.')
add_bullets([
    'Separate bars represent Hybrid, Quantum and Predictive.',
    'The x-axis identifies modes.',
    'The y-axis represents unmet demand in patient-hours.',
    'The chart starts at zero to avoid a misleading visual scale.',
    'A plain-language verdict summarizes the measured winner.',
    'Recent metrics show the live state and operational results.'
])
add_p('Low unmet demand is generally better. The chart should be interpreted using exact numbers, not only color or bar height.')

add_heading('15.4 Failure Lab', 2)
add_p('Purpose: find and replay threshold failures under controlled disruption scenarios.')
add_bullets([
    'Admission surge',
    'Nurse shortage',
    'Bed closure',
    'ED overload'
])
add_p('The backend runs each scenario across multiple seeds and all three modes. The failure detector identifies a block when a configured threshold is exceeded. Failure blocks are grouped by mode and contain the start hour, end hour, department, root cause and evidence.')
add_p('Important example: Hybrid and Predictive can show many forecast-miss blocks, while Quantum can show a small number of capacity or staffing blocks. The exact result depends on the selected seeds and horizon.')
add_p('The page should not use “most failures means one mode is universally worse” by itself. Compare count, duration, severity, unmet demand and recovery context.')

add_heading('15.5 Settings', 2)
add_p('Purpose: configure live simulation values and explain that changing settings affects future or reset state.')
add_bullets([
    'Seed selects reproducible randomness.',
    'Horizon controls how many hourly steps are used.',
    'Speed controls playback.',
    'Mode changes the allocation policy.',
    'Disruption selection or injection creates stress conditions.'
])
add_p('The settings endpoint sends the seed and horizon to FastAPI and returns the updated HospitalState.')

add_heading('15.6 Methodology', 2)
add_p('Purpose: explain the data, assumptions, process, mathematical model and limitations.')
add_p('It should show that this is a synthetic research simulator, not an empirical clinical study. It also communicates that the Qiskit QAOA solver is optional and that the normal multi-hour comparison uses local neal simulated annealing.')

add_heading('15.7 Dashboard of measured evidence', 2)
add_p('Any image or chart used for the presentation should show exact values and the scenario. For example, 48-hour or 72-hour unmet-demand comparisons can differ, so always state the horizon and seed.')

add_heading('16. Backend API endpoints', 1)
add_table(['Endpoint', 'Method', 'Purpose'], [
    ('/health', 'GET', 'Check that the server is alive'),
    ('/simulation/state', 'GET', 'Retrieve the current hospital state'),
    ('/simulation/start', 'POST', 'Start or initialize a run'),
    ('/simulation/pause', 'POST', 'Pause the simulation'),
    ('/simulation/reset', 'POST', 'Reset the simulation'),
    ('/simulation/step', 'POST', 'Advance one hour'),
    ('/simulation/mode', 'POST', 'Change allocation mode'),
    ('/simulation/settings', 'POST', 'Update seed and horizon'),
    ('/simulation/events', 'POST', 'Inject a disruption'),
    ('/metrics', 'GET', 'Retrieve metrics'),
    ('/comparison', 'GET', 'Run or return comparison results'),
    ('/comparison/run', 'POST', 'Start an asynchronous comparison job'),
    ('/comparison/{id}', 'GET', 'Check comparison job status'),
    ('/failures', 'GET', 'Return matched failure evidence'),
    ('/ws/state', 'WebSocket', 'Receive live state updates'),
])
add_p('FastAPI provides interactive API documentation at /docs and ReDoc documentation at /redoc. OpenAPI JSON is available at /openapi.json.')

add_heading('17. Running the project', 1)
add_heading('Local development', 2)
add_code('Terminal 1: backend\n.venv\\Scripts\\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001\n\nTerminal 2: frontend\nnpm --prefix frontend run dev')
add_p('Open the frontend at http://127.0.0.1:5173 and the API documentation at http://127.0.0.1:8001/docs.')
add_heading('Docker', 2)
add_code('Copy-Item .env.example .env\ndocker compose up --build')
add_p('Docker exposes the frontend on 5173 and the backend on 8001 in the project configuration.')

add_heading('18. Use cases', 1)
add_table(['Use case', 'How the project applies', 'Value'], [
    ('Hospital surge planning', 'Run admissions surge and ED overload', 'Study queue growth and recovery'),
    ('Staff shortage testing', 'Remove nurse availability', 'Compare the response of each mode'),
    ('Bed closure simulation', 'Close beds in a selected department', 'Observe downstream queue pressure'),
    ('Capacity planning education', 'Change seed and horizon', 'Teach reproducible scenario analysis'),
    ('Optimization comparison', 'Run matched mode experiments', 'Compare greedy, QUBO and hybrid policies'),
    ('Forecast evaluation', 'Inspect MAPE and unmet demand', 'Understand forecast impact'),
    ('Failure analysis', 'Open the Failure Lab', 'Identify threshold violations and replay causes'),
    ('Presentation and viva demonstration', 'Use live controls and charts', 'Make the project easy to explain and verify'),
])

add_heading('19. Real-world applications', 1)
add_bullets([
    'Hospital operations research and scenario planning',
    'Nurse shift allocation experiments',
    'Emergency capacity planning',
    'Bed utilization and queue research',
    'Demand forecasting demonstrations',
    'AI and optimization teaching',
    'Disaster or seasonal surge preparation',
    'What-if simulations before policy changes'
])
add_p('A real implementation would require clinical validation, a secure data system, staff and bed constraints, privacy controls, audit logs, role-based access and human approval before deployment.')

add_heading('20. Why the project is suitable for a Level Year or degree project', 1)
add_bullets([
    'It combines more than one discipline: healthcare operations, forecasting, optimization, web systems and visualization.',
    'It has a clear research question and measurable outputs.',
    'It uses reproducible seeds and matched scenarios.',
    'It includes a backend and frontend, not only an algorithm.',
    'It demonstrates a practical problem, but remains legal and safe to test with synthetic data.',
    'It supports several levels of explanation: basic, technical and mathematical.',
    'It contains experiments, limitations and future work instead of a purely success-focused narrative.',
    'It is possible to extend it with a real dataset or stronger forecasting model.',
    'It has clear page-based demonstrations for review and viva.'
])

add_heading('21. Why the Hybrid approach can be best', 1)
add_p('Hybrid is strongest because it does not depend on one kind of information. It combines forecast demand, queue pressure and optimization constraints, then replans as conditions change.')
add_bullets([
    'Forecasting helps it prepare for expected future demand.',
    'CP-SAT applies limits and balances staff efficiently.',
    'Queue pressure makes it respond to a problem that is already visible.',
    'Hourly replanning allows it to recover after a disruption.',
    'A mismatch in the forecast does not stop the system from reacting to reality.',
    'Bed-state and queue logic complement nurse optimization.'
])
add_callout('Fair claim', 'Hybrid is designed to be more adaptive and may show better measured unmet-demand or recovery results in a matched scenario. This is a demonstration claim for the synthetic experiment, not proof that Hybrid is universally superior.', 'FFF4E5')

add_heading('22. Why the result must be judged carefully', 1)
add_bullets([
    'Only synthetic data is used.',
    'A small number of seeds is used.',
    'The experiment has a fixed 72-hour default unless changed.',
    'Disruptions follow fixed start times and durations.',
    'Forecast models and staffing rules are simplified.',
    'Bed optimization and nurse optimization are encoded at different levels.',
    'Runtime is affected by the local computer.',
    'No statistical significance or clinical conclusion is claimed.'
])

add_heading('23. Existing measured evidence', 1)
add_p('One example from the project’s 72-hour local result shows Hybrid with 423 unmet patient-hours, Quantum with 544 and Predictive with 986. These numbers should be identified as measured for that seed, horizon and scenario, not as universal performance figures.')
add_table(['Mode', 'Example unmet patient-hours', 'Interpretation'], [
    ('Hybrid', '423', 'Lowest example unmet demand'),
    ('Quantum-inspired', '544', 'Higher than Hybrid in this example'),
    ('Predictive', '986', 'Highest example unmet demand'),
])
add_p('A 48-hour measured example reported 245 unmet hours for Hybrid, 306 for Quantum and 466 for Predictive. Always state the horizon, because extending the run can change totals.')

add_heading('24. Explain Failure Lab evidence correctly', 1)
add_p('One Failure Lab screenshot may show 523 Hybrid failures, 8 Quantum failures and 504 Predictive failures. This number represents detected threshold blocks for the selected scenario and seeds.')
add_p('The correct explanation is:')
add_callout('Example explanation', 'For the selected admission-surge scenario and seed set, Quantum produced 8 detected failure blocks covering 11 failure-hours, while Hybrid and Predictive had substantially more forecast or operational threshold violations. The report is evidence for that matched run only.', 'EEF6FA')
add_p('The Failure Lab verdict that names the longest block means “longest observed failure block,” not “best overall policy.” The main dashboard comparison and unmet-demand metric should be used for the overall performance statement.')

add_heading('25. Simple comparison of evidence terms', 1)
add_table(['Term', 'Simple meaning'], [
    ('Unmet demand', 'Patient demand that the system could not satisfy'),
    ('Patient-hours', 'Unmet patients accumulated over hours'),
    ('Bed utilization', 'Percentage of available beds occupied'),
    ('Nurse balance', 'How unevenly staff workload is distributed'),
    ('Final queue', 'Patients still waiting at the end'),
    ('MAPE', 'Average percentage forecast error'),
    ('Failure block', 'A period during which an operating threshold is exceeded'),
    ('Seed', 'Starting value that makes random behavior repeatable'),
    ('Horizon', 'Number of hourly simulation steps'),
])

add_heading('26. Test and validation', 1)
add_bullets([
    'Backend pytest suite for API and simulation behavior',
    'Failure detector tests',
    'Optimization tests for CP-SAT and solvers',
    'Predictive model tests',
    'Frontend TypeScript compilation',
    'Frontend Vitest tests',
    'HTTP health and route checks',
    'CORS and live server checks'
])
add_p('A successful test proves the tested function behaves correctly; it does not prove the whole hospital model is clinically valid.')

add_heading('27. Limitations', 1)
add_bullets([
    'Synthetic data is not real patient data.',
    'The four departments are simplified.',
    'Nurse staffing rules are not clinically validated.',
    'The QUBO optimizes nurse allocation but does not encode every bed or patient decision.',
    'The normal Quantum mode is quantum-inspired because it uses local neal simulated annealing.',
    'Qiskit QAOA is optional and expensive; it is not the baseline comparison.',
    'The API stores one in-memory simulation per process.',
    'The dashboard should not be used for real medical decisions.',
    'The system has no production authentication or multi-user isolation.',
    'A large external dataset is not included.'
])

add_heading('28. Future improvements', 1)
add_bullets([
    'Use a validated real or de-identified aggregate dataset.',
    'Compare larger horizons and more seeds.',
    'Use confidence intervals and formal statistical tests.',
    'Add a complete bed-allocation QUBO and mixed-integer model.',
    'Use real cloud or quantum hardware for selected experiments.',
    'Add actual versus forecast accuracy for every department.',
    'Store multiple users and simulation sessions in a database.',
    'Add authentication and role-based access.',
    'Build clinician-approved staffing constraints.',
    'Add cost, fairness and patient-risk objectives.',
    'Export PDFs, audit logs and repeatable experiment reports.',
    'Deploy as Docker containers behind an HTTPS gateway.'
])

add_heading('29. Viva questions and answers', 1)

qa = [
('What is the project about?', 'It is a hospital operations simulation that compares three resource-allocation approaches under the same synthetic demand and disruption conditions.'),
('Why are there three modes?', 'To compare forecast-only, quantum-inspired binary optimization and hybrid forecast-plus-live-queue allocation.'),
('What is the Hybrid approach?', 'It combines predictive forecasting, OR-Tools constraint optimization and real-time replanning after every hour and disruption.'),
('Why is it called Dynamic?', 'It recalculates the allocation instead of relying on one fixed plan.'),
('What is a seed?', 'A starting value for random number generation that makes an experiment repeatable.'),
('What is a horizon?', 'The number of hourly simulation steps or the total period to run.'),
('What is unmet demand?', 'Demand that cannot be served because the hospital lacks sufficient bed or operational capacity.'),
('What is bed utilization?', 'The proportion of available beds that are occupied.'),
('What is MAPE?', 'Mean Absolute Percentage Error. It measures average percentage distance between forecast and actual value.'),
('What is a QUBO?', 'Quadratic Unconstrained Binary Optimization: a mathematical model in which binary variables represent decisions and constraints become penalties.'),
('Does your Quantum mode use real quantum hardware?', 'No. The normal multi-hour comparison uses local Ocean/neal simulated annealing. Qiskit QAOA can run locally on Aer for small experiments.'),
('How does the Hybrid solver work?', 'It uses OR-Tools CP-SAT to allocate nurses under limits, with forecast and queue objectives, and recalculates each hour.'),
('What is OR-Tools?', 'A Google optimization library that provides constraint programming and integer optimization tools.'),
('What is CP-SAT?', 'Constraint Programming - Satisfiability, a solver that finds feasible or optimal values while respecting constraints.'),
('How do you make comparisons fair?', 'The same seed, horizon, department capacity and disruption scenario are provided to every mode.'),
('Which mode is best?', 'In the example 72-hour result, Hybrid had the lowest unmet demand, but no universal conclusion is claimed.'),
('Why might Hybrid be better?', 'It uses forecast information and live queue pressure while continuously repairing plans after changes.'),
('What did the Failure Lab show?', 'Different modes produce different threshold violations. Quantum can have fewer blocks in one selected seed set, while forecast-based modes may show many forecast-miss blocks.'),
('Why can the Failure Lab verdict be confusing?', 'The longest failure block is not the same as lowest unmet demand or the mode with the fewest failures.'),
('What is a REST API?', 'A web interface where the frontend sends HTTP requests to retrieve or change backend state.'),
('What is CORS?', 'Cross-Origin Resource Sharing controls which frontend origins are allowed to call the backend API.'),
('What is FastAPI?', 'A Python framework for creating HTTP APIs with automatic validation and documentation.'),
('What is Zustand?', 'A small frontend state manager used to store simulation mode, state and busy status.'),
('What is Plotly used for?', 'Rendering interactive comparison charts and operational metrics.'),
('What is Phaser used for?', 'Displaying the simulated hospital scene in the browser.'),
('What are the main weaknesses?', 'The data is synthetic, staffing rules are simplified, the sample size is small and no clinical validation has occurred.'),
('What future work would you add?', 'Validated data, more statistical analysis, larger horizons, persistent multi-user storage and clinician-reviewed constraints.'),
('Why is this suitable for a project?', 'It combines research, data, modeling, optimization, backend and frontend systems into a measurable and demonstrable application.'),
('Can it be used in a real hospital today?', 'No. It is explicitly a research and demonstration system, not clinical decision-support software.'),
]
for question, answer in qa:
    add_heading(question, 2)
    add_p(answer)

add_heading('30. Short 2-minute presentation script', 1)
add_p('“Good morning. This project is an Adaptive Healthcare Operations Intelligence Platform. A hospital has four departments: General Medicine, Cardiology, Neurology and Orthopedics. Patient arrivals and resource availability change every hour.”')
add_p('“The application models beds, nurses, patient queues and disruptions. The backend uses Python and FastAPI. The frontend uses React, TypeScript, Phaser and Plotly.”')
add_p('“We compare three policies. Predictive AI allocates staff based on forecast demand. Quantum Optimization creates a QUBO nurse-allocation problem and uses local quantum-inspired annealing. Hybrid combines forecast demand, queue pressure and constraint optimization using OR-Tools CP-SAT.”')
add_p('“The simulation is matched. The same seed, horizon and disruption are applied to every mode. This makes the comparison reproducible. The dashboard shows unmet demand, utilization and other operational metrics. The Failure Lab identifies threshold breaches and allows replay of the strongest evidence.”')
add_p('“In one 72-hour matched example, Hybrid produced 423 unmet patient-hours, Quantum produced 544, and Predictive produced 986. These are synthetic results, not clinical proof.”')
add_p('“Hybrid is useful because it prepares from forecasts but also replans with live queues and disruptions. It combines planning and reaction instead of relying on one fixed decision.”')
add_p('“The project is suitable for a degree project because it is end-to-end, measurable, reproducible and expandable. It also has clear limitations. The data is synthetic, the rules are simplified and the system is not ready for real patient care.”')

add_heading('31. Short 30-second summary', 1)
add_callout('Final summary', 'The project is a synthetic hospital operations simulator that compares Predictive AI, quantum-inspired QUBO optimization and a Dynamic Hybrid approach. It runs matched scenarios, measures unmet demand and failures, visualizes live hospital state and explains the measured result. Hybrid is the most adaptive because it combines forecasting, constrained optimization and continuous replanning. The project is suitable for research and academic demonstration, but not for real clinical decisions.', 'EAF7F5')

add_heading('32. Recommended wording for honest conclusions', 1)
add_table(['Avoid', 'Use instead'], [
    ('Quantum is better', 'Quantum-inspired mode performed better in this particular synthetic result'),
    ('Quantum has an advantage', 'The normal local solver used quantum-inspired simulated annealing, not quantum hardware'),
    ('Hybrid always wins', 'Hybrid showed lower unmet demand in these measured examples'),
    ('The failure result proves success', 'The result is evidence for the selected scenario, seed and horizon'),
    ('This is clinically useful', 'This is a research demo that requires clinical validation'),
])

# Footer
for sec in doc.sections:
    footer = sec.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Adaptive Healthcare Operations Intelligence Platform - Exam Review')
    r.font.size = Pt(8)
    r.font.color.rgb = RGBColor.from_string('667085')

# Core properties
doc.core_properties.title = 'Adaptive Healthcare Operations Intelligence Platform - Exam Review'
doc.core_properties.subject = 'Project story, architecture, technical guide and viva preparation'
doc.core_properties.author = 'Project Exam Review Guide'

doc.save(OUT)
print(str(OUT))
