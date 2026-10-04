import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pickle
from datetime import date
import plotly.express as px


#Initializing Setup and Saving Basic variables
st.set_page_config(page_title="MapMyALS", layout="wide", initial_sidebar_state="expanded")

#Medical card style to overwrite exisiting Streamlit settings - made by AI
st.markdown("""
    <style>
        /* For the background */
        .stApp {background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;}

        /* Dark Slate theme in the sidebar */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
            box-shadow: 4px 0px 15px rgba(0, 0, 0, 0.05);
        }
        [data-testid="stSidebar"] *, [data-testid="stSidebarNav"] * {
            color: #f1f5f9 !important;
        }

        /* White floating cards to match the medical-grade cards */
        .medical-card {
            background-color: #ffffff;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
        }

        /* Better buttons */
        .stButton>button {
            border-radius: 8px;
            background-color: #2563eb !important;
            color: white !important;
            border: none;
        }

        /* Hide streamlit default footers/headers */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

if "followUpLog" not in st.session_state:
    st.session_state.followUpLog = []
if "baseline_date" not in st.session_state:
    st.session_state.baseline_date = date.today()

if "saved_age" not in st.session_state: st.session_state.saved_age = 55
if "saved_sex" not in st.session_state: st.session_state.saved_sex = "Male"
if "saved_onset" not in st.session_state: st.session_state.saved_onset = "Limb"
if "saved_riluzole" not in st.session_state: st.session_state.saved_riluzole = "Yes"

if "bulbar_baseline" not in st.session_state: st.session_state.bulbar_baseline = 12
if "fine_motor_baseline" not in st.session_state: st.session_state.fine_motor_baseline = 12
if "gross_motor_baseline" not in st.session_state: st.session_state.gross_motor_baseline = 12
if "respiratory_baseline" not in st.session_state: st.session_state.respiratory_baseline = 12
if "alsfrs_baseline" not in st.session_state: st.session_state.alsfrs_baseline = 12


if "predicted_alsfrs_slope" not in st.session_state: st.session_state.predicted_alsfrs_slope = 0
if "predicted_bulbar_slope" not in st.session_state: st.session_state.predicted_bulbar_slope = 0
if "predicted_fine_motor_slope" not in st.session_state: st.session_state.predicted_fine_motor_slope = 0
if "predicted_gross_motor_slope" not in st.session_state: st.session_state.predicted_gross_motor_slope = 0
if "predicted_respiratory_slope" not in st.session_state: st.session_state.predicted_respiratory_slope = 0

#Used AI to write the exact syntax of pickle.load(open(...))
@st.cache_resource
def get_model():
    return pickle.load(open('als_progression_model.pkl', 'rb'))

loaded_model = get_model()

def update_model():
  feed_into_model = {
        'Age': [st.session_state.saved_age], 
        'ALSFRS_R_Baseline': [st.session_state.alsfrs_baseline], 
        'Bulbar_Baseline': [st.session_state.bulbar_baseline],
        'Fine_Motor_Baseline': [st.session_state.fine_motor_baseline], 
        'Gross_Motor_Baseline': [st.session_state.gross_motor_baseline], 
        'Respiratory_Baseline': [st.session_state.respiratory_baseline],
        'Sex_Male': [1 if st.session_state.saved_sex == 'Male' else 0], 
        'Site_of_Onset_Limb': [1 if st.session_state.saved_onset == 'Limb' else 0], 
        'Site_of_Onset_Other/Mixed': [1 if st.session_state.saved_onset == 'Other/Mixed' else 0], 
        'Riluzole_Unknown': [1 if st.session_state.saved_riluzole == 'Unknown' else 0], 
        'Riluzole_Yes': [1 if st.session_state.saved_riluzole == 'Yes' else 0]
    }
  
  changed_df = pd.DataFrame(feed_into_model)

  predicted_slopes = loaded_model.predict(changed_df)
  st.session_state.predicted_alsfrs_slope = predicted_slopes[0][0]
  st.session_state.predicted_bulbar_slope = predicted_slopes[0][1]
  st.session_state.predicted_fine_motor_slope = predicted_slopes[0][2]
  st.session_state.predicted_gross_motor_slope = predicted_slopes[0][3]
  st.session_state.predicted_respiratory_slope = predicted_slopes[0][4]


def home():
  st.markdown('<div class="medical-card">', unsafe_allow_html=True)
  st.title("Welcome to MapMyALS Portal")

  st.subheader("""
    Welcome to **MapMyALS**, a healthcare platform to guide and help provide support to patients, families, and caregivers navigating the progression of ALS across the Bay Area.
    """)
  information, howToNavigate = st.columns([1.5, 1])
  with information:
    st.markdown("""
    ### How Does This App Help You?
    * **Personalized Progression Charts:** You are able to view a simple, visual timeline of predicted clinical scores to plan ahead and avoid surprises.
    * **Predictive Intervention Alerts:** Friendly notifications about looking into assistive tools to plan ahead before reaching an emergency situation.
    * **Local Resource Finder:** Locate exactly where to borrow equipment, join support groups, or access care centers near you in San Mateo Country.
    """)
  with howToNavigate:
    st.markdown("""
    ### Follow These Next Steps to Get Started:
    * **1. Open User Profile and Charts** on the sidebar to enter patient baseline information and clinical scores
    * **2. Add Follow-up Appointments** with new scores to ensure accurate alerts and track your status.
    * **3. Visit Alerts & Support Maps** to receive helpful reminders about assistance or adaptive technology.

    """)

  st.markdown("**Disclaimer:** This app is for informational purposes only and is not medically verified. Always consult with your doctor or a qualified healthcare provider before making any changes to your treatment plan.")
  st.markdown('</div>', unsafe_allow_html=True)

def alsfrs_explanation():
  #Used AI to make the card styling in html
  st.html("""
        <style>
        .main-title h1, .main-title h2, .main-title h3, .main-title p {
            color: #111111;
        }
        </style>
    """)
  
  st.title("ALSFRS-R Breakdown Explanation")
  st.subheader("What is an ALSFRS-R Score?")
  st.write("ALSFRS-R score is a 12 question aggregate score used by doctors to measure physical function and track disease progression in people with ALS. Scores range from 0 to 48, where a higher score signifies greater functional abilities across speech, movement, and breathing subcategories.")

  def make_explanation(title, bg_color,cat1,cat2,cat3,text1_3,text1_2,text1_1,text1_0,text2_3,text2_2,text2_1,text2_0,text3_3,text3_2,text3_1,text3_0):
    
    #Used AI to make the card styling in html
    st.html(f"""
        <div style="
            background-color: {bg_color}; 
            border: 1px solid rgba(0, 0, 0, 0.1); 
            border-radius: 16px; 
            padding: 24px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
            margin-bottom: 24px;
            color: #000000;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        ">
            <h3 style="color: #000000; margin-top: 0; font-size: 1.35rem;">{title}</h3>
            
            <p style="margin-bottom: 4px; font-weight: bold;">{cat1}</p>
            <p style="font-size: 0.95rem; line-height: 1.4; margin-top: 0; margin-bottom: 16px; white-space: pre-line;">
                <strong>4:</strong> Normal
                <strong>3:</strong> {text1_3}
                <strong>2:</strong> {text1_2}
                <strong>1:</strong> {text1_1}
                <strong>0:</strong> {text1_0}
            </p>

            <p style="margin-bottom: 4px; font-weight: bold;">{cat2}</p>
            <p style="font-size: 0.95rem; line-height: 1.4; margin-top: 0; margin-bottom: 16px; white-space: pre-line;">
                <strong>4:</strong> Normal
                <strong>3:</strong> {text2_3}
                <strong>2:</strong> {text2_2}
                <strong>1:</strong> {text2_1}
                <strong>0:</strong> {text2_0}
            </p>

            <p style="margin-bottom: 4px; font-weight: bold;">{cat3}</p>
            <p style="font-size: 0.95rem; line-height: 1.4; margin-top: 0; margin-bottom: 0; white-space: pre-line;">
                <strong>4:</strong> Normal
                <strong>3:</strong> {text3_3}
                <strong>2:</strong> {text3_2}
                <strong>1:</strong> {text3_1}
                <strong>0:</strong> {text3_0}
            </p>
        </div>
    """)
      

  left, right = st.columns(2)

  with left:
    make_explanation(
        "Bulbar",
        "#FFF2EB",
        "Speech",
        "Salivation",
        "Swallowing",
        "Detectable speech disturbance",
        "Intelligible with repeating",
        "Speech combined with nonvocal communication",
        "Loss of useful speech",
        "Slight but definite excess of saliva in mouth; may have nighttime drooling",
        "Moderately excessive saliva; may have minimal drooling",
        "Marked excess of saliva with some drooling",
        "Marked drooling; requires constant tissue or handkerchief",
        "Early eating problems — occasional choking",
        "Dietary consistency changes",
        "Needs supplemental tube feeding",
        "NPO (exclusively parenteral or enteral feeding)"
    )

    make_explanation(
        "Fine Motor",
        "#EBFBF5",
        "Handwriting",
        "Cutting with Food",
        "Dressing and Hygiene",
        "Slow or sloppy: all words are legible",
        "Not all words are legible",
        "Able to grip pen but unable to write",
        "Unable to grip pen",
        "Somewhat slow and clumsy, but no help needed",
        "Can cut most foods, although clumsy and slow; some help needed",
        "Food must be cut by someone, but can still feed slowly",
        "Needs to be fed",
        "Independent and complete self-care with effort or decreased efficiency",
        "Intermittent assistance or substitute methods",
        "Needs attendant for self-care",
        "Total dependence"
    )

  with right:
    make_explanation(
        "Gross Motor",
        "#F3EFFF",
        "Turning in Bed",
        "Walking",
        "Climbing Stairs",
        "Somewhat slow and clumsy, but no help needed",
        "Can turn alone or adjust sheets, but with great difficulty",
        "Can initiate, but not turn or adjust sheets alone",
        "Helpless",
        "Early ambulation difficulties",
        "Walks with assistance",
        "Nonambulatory functional movement",
        "No purposeful leg movement",
        "Slow",
        "Mild unsteadiness or fatigue",
        "Needs assistance",
        "Cannot do"
    )

    make_explanation(
        "Respiratory",
        "#FFF0F5",
        "Dyspnea",
        "Orthopnea",
        "Respiratory Insufficiency",
        "Occurs when walking",
        "Occurs with one or more of the following: eating, bathing, dressing (ADL)",
        "Occurs at rest, difficulty breathing when either sitting or lying",
        "Significant difficulty, considering using mechanical respiratory support",
        "Some difficulty sleeping at night due to shortness of breath, does not routinely use more than two pillows",
        "Needs extra pillows in order to sleep (more than two)",
        "Can only sleep sitting up",
        "Unable to sleep",
        "Intermittent use of BiPAP",
        "Continuous use of BiPAP during the night",
        "Continuous use of BiPAP during the night and day",
        "Invasive mechanical ventilation by intubation or tracheostomy"
    )

  st.markdown("**Reference:** Cedarbaum JM, Stambler N, Malta E, et al. The ALSFRS-R: a revised ALS functional rating scale that incorporates assessments of respiratory function. *J Neurol Sci*. 1999;169(1-2):13-21.")

questions_saved = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "r1", "r2", "r3"]
for i in questions_saved:
  check_saved = f"baseline_{i}"
  if check_saved not in st.session_state:
    st.session_state[check_saved] = 4

#function written with the help of AI (used for syntax of st.session_state.get() function)
def subscore_questions(unique_key, defaults = 2):
    st.caption("Rate from 4 (Normal Function) to 0 (Severe Impairment)")

    with st.expander("Bulbar Symptoms (Speech & Swallowing)"):
        saved_q1 = st.session_state.get(f"{unique_key}_q1", defaults)
        q1 = st.slider("Q1: Speech", 0, 4, value=saved_q1, key=f"{unique_key}_q1")
        saved_q2 = st.session_state.get(f"{unique_key}_q2", defaults)
        q2 = st.slider("Q2: Salivation", 0, 4, value =saved_q2, key=f"{unique_key}_q2")
        saved_q3 = st.session_state.get(f"{unique_key}_q3", defaults)
        q3 = st.slider("Q3: Swallowing", 0, 4, value = saved_q3, key=f"{unique_key}_q3")
        b_sum = q1 + q2 + q3
        st.metric("Bulbar Total", f"{b_sum} / 12")

    with st.expander("Fine Motor Skills (Handwriting & Dressing)"):
        saved_q4 = st.session_state.get(f"{unique_key}_q4", defaults)
        q4 = st.slider("Q4: Handwriting", 0, 4, value = saved_q4, key=f"{unique_key}_q4")

        saved_q5 = st.session_state.get(f"{unique_key}_q5", defaults)
        q5 = st.slider("Q5: Cutting Food", 0, 4, value = saved_q5, key=f"{unique_key}_q5")

        saved_q6 = st.session_state.get(f"{unique_key}_q6", defaults)
        q6 = st.slider("Q6: Dressing & Personal Hygiene", 0, 4, value = saved_q6, key=f"{unique_key}_q6")
        f_sum = q4 + q5 + q6
        st.metric("Fine Motor Total", f"{f_sum} / 12")

    with st.expander("Gross Motor Skills (Walking & Stairs)"):
        saved_q7 = st.session_state.get(f"{unique_key}_q7", defaults)
        q7 = st.slider("Q7: Turning in Bed / Clothes", 0, 4, value = saved_q7, key=f"{unique_key}_q7")

        saved_q8 = st.session_state.get(f"{unique_key}_q8", defaults)
        q8 = st.slider("Q8: Walking", 0, 4, value = saved_q8, key=f"{unique_key}_q8")

        saved_q9 = st.session_state.get(f"{unique_key}_q9", defaults)
        q9 = st.slider("Q9: Climbing Stairs", 0, 4, value = saved_q9, key=f"{unique_key}_q9")
        g_sum = q7 + q8 + q9
        st.metric("Gross Motor Total", f"{g_sum} / 12")

    with st.expander("Respiratory Function (Breathing)"):
        saved_r1 = st.session_state.get(f"{unique_key}_r1", defaults)
        r1 = st.slider("R1: Dyspnea (Shortness of Breath)", 0, 4, value = saved_r1, key=f"{unique_key}_r1")

        saved_r2 = st.session_state.get(f"{unique_key}_r2", defaults)
        r2 = st.slider("R2: Orthopnea (Breathing Lying Flat)", 0, 4, value = saved_r2, key=f"{unique_key}_r2")

        saved_r3 = st.session_state.get(f"{unique_key}_r3", defaults)
        r3 = st.slider("R3: Respiratory Insufficiency", 0, 4, value = saved_r3, key=f"{unique_key}_r3")
        r_sum = r1 + r2 + r3
        st.metric("Respiratory Total", f"{r_sum} / 12")

    questions_to_save = [q1,q2,q3,q4,q5,q6,q7,q8,q9,r1,r2,r3]

    return b_sum, f_sum, g_sum, r_sum, questions_to_save


@st.dialog("Add a Follow-Up Appointment")
def new_log():
  st.markdown("Enter information from your follow-up checkup below.")
  appointment_date = st.date_input("Appointment Date", value = date.today())

  days_passed = abs((appointment_date-st.session_state.get("baseline_date")).days)
  if appointment_date < st.session_state.get("baseline_date"):
    st.warning("This is *before* your baseline appointment date.")
  else:
    st.info(f"This is **{days_passed} days** after your baseline appointment date.")


  b_s, f_s, g_s, r_s, k= subscore_questions(unique_key="new", defaults=4)
  alsfrs_total = b_s + f_s + g_s + r_s

  if st.button("Add Entry to Chart"):
    st.session_state.followUpLog.append({
        "Date": appointment_date,
        "Days Passed": days_passed,
        "Total ALSFRS-R Score": alsfrs_total,
        "Bulbar": b_s,
        "Fine Motor": f_s,
        "Gross Motor": g_s,
        "Respiratory": r_s
    })

    #Added by AI after troubleshooting to rerun and save/sort this new addition
    st.session_state.followUpLog = sorted(st.session_state.followUpLog, key=lambda x: x['Date'])
    st.rerun()

def user_charts():
  st.title("Your Profile & Charts")
  st.markdown("Enter your baseline information below to view your personalized 12-month timeline charts.")

  input_area, graph_area = st.columns([1,1.3])

  with input_area:
    st.markdown('<div class="medical-card">', unsafe_allow_html=True)
    st.subheader("Initial Patient Information")

    col1, col2 = st.columns([1,1])

    with col1:
      age = st.number_input("Age", min_value=18, max_value=95, key = "saved_age")
      sex = st.selectbox("Biological Sex", ["Male", "Female"], key="saved_sex")
    with col2:
      onset = st.selectbox("Site of Onset", ["Limb", "Bulbar", "Other/Mixed"], key="saved_onset")
      riluzole = st.selectbox("Taking Riluzole?", ["Yes", "No", "Unknown"], key="saved_riluzole")

    base_date = st.date_input("Initial Evaluation Date", key="baseline_date")

    base_bulbar, base_fine_motor, base_gross_motor, base_respiratory, list_questions = subscore_questions(unique_key = "baseline", defaults = 4)
    base_alsfrs_total = base_bulbar+ base_fine_motor+ base_gross_motor+ base_respiratory

    # st.session_state.saved_age = age
    # st.session_state.saved_sex = sex
    # st.session_state.saved_onset = onset
    # st.session_state.saved_riluzole = riluzole
    # st.session_state.baseline_date = base_date

    st.session_state.bulbar_baseline = base_bulbar
    st.session_state.fine_motor_baseline = base_fine_motor
    st.session_state.gross_motor_baseline = base_gross_motor
    st.session_state.respiratory_baseline = base_respiratory
    st.session_state.alsfrs_baseline = base_alsfrs_total

    update_model()

    # questions_saved = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "r1", "r2", "r3"]
    # for index,name in enumerate(questions_saved):
    #   fullName = f"baseline_{name}"
    #   st.session_state[fullName] = list_questions[index]

    st.metric(label="Initial ALSFRS-R Score", value=f"{base_alsfrs_total} / 48")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("+ Add New Follow-Up Log",  use_container_width= True):
        new_log()

    st.subheader("Your Historical Clinical Logs")
    if not st.session_state.followUpLog:
      st.markdown("No follow-up entries logged yet. Click the button above to add your first visit to your chart.")
    else:
      #used AI to generate a rough draft of this block as it loops through the followUpLog
      for idx, entry in enumerate(st.session_state.followUpLog):
        card_title = f"Visit: {entry['Date'].strftime('%B %d, %Y')}"
        with st.expander(card_title):
          st.write(f"**Days Since Initial Evaluation Baseline:** {entry['Days Passed']} days")
          c1, c2, c3, c4 = st.columns([1,1,1,1])
          c1.metric("Bulbar", f"{entry['Bulbar']}/12")
          c2.metric("Fine Motor", f"{entry['Fine Motor']}/12")
          c3.metric("Gross Motor", f"{entry['Gross Motor']}/12")
          c4.metric("Respiratory", f"{entry['Respiratory']}/12")
          if st.button("🗑️ Delete This Card", key=f"del_{idx}", use_container_width = True):
            st.session_state.followUpLog.pop(idx)
            st.rerun()

  with graph_area:
      st.markdown('<div class="medical-card">', unsafe_allow_html=True)
      st.subheader("Your Personalized Predicted Trajectory")
      days_timeline = np.array(range(0, 366))


      daily_alsfrs_slope = st.session_state.predicted_alsfrs_slope
      daily_bulbar_slope = st.session_state.predicted_bulbar_slope
      daily_fine_motor_slope = st.session_state.predicted_fine_motor_slope
      daily_gross_motor_slope = st.session_state.predicted_gross_motor_slope
      daily_respiratory_slope = st.session_state.predicted_respiratory_slope

      y_alsfrs = np.clip(base_alsfrs_total + (daily_alsfrs_slope * days_timeline), 0, 48)
      y_bulbar = np.clip(base_bulbar + (daily_bulbar_slope * days_timeline), 0, 12)
      y_fine_motor = np.clip(base_fine_motor + (daily_fine_motor_slope * days_timeline), 0, 12)
      y_gross_motor = np.clip(base_gross_motor + (daily_gross_motor_slope * days_timeline), 0, 12)
      y_respiratory = np.clip(base_respiratory + (daily_respiratory_slope * days_timeline), 0, 12)

      #function built with the help of AI to build base of graph + adjust the colors and layout/appearances
      def build_graph(timeline_y, baseline_val, title_text, y_max, trace_color, line_style='solid'):
        f = go.Figure()
        f.add_trace(go.Scatter(x=days_timeline, y=timeline_y, mode='lines', name='Predicted Slope', line=dict(color=trace_color, width=3, dash=line_style)))
        f.add_trace(go.Scatter(x=[0], y=[baseline_val], mode='markers', name='Baseline Start', marker=dict(color=trace_color, size=12, symbol='diamond', line=dict(color='white', width=1.5))))
        f.update_layout(
          title=dict(text=title_text, font=dict(size=14, color='#1e293b')),
          xaxis_title="Days Elapsed", yaxis_title="Score",
          showlegend=False, margin=dict(l=15, r=15, t=35, b=15),
          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
          xaxis=dict(showgrid=True, gridcolor='#e2e8f0', range=[-10, 380], tickmode='array', tickvals= [0, 30, 60, 90, 180, 270, 365]),
          yaxis=dict(showgrid=True, gridcolor='#e2e8f0', range=[-0.5, y_max + 0.5])
          )
        return f

      alsfrs_graph = build_graph(y_alsfrs, base_alsfrs_total, "Main ALSFRS-R Aggregate Trajectory (0-48)", 48, '#2563eb')
      bulbar_graph = build_graph(y_bulbar, base_bulbar, "Bulbar Subscore Tracking (0-12)", 12, '#ea580c')
      fine_motor_graph  = build_graph(y_fine_motor, base_fine_motor, "Fine Motor Subscore Tracking (0-12)", 12, '#10b981')
      gross_motor_graph  = build_graph(y_gross_motor, base_gross_motor, "Gross Motor Subscore Tracking (0-12)", 12, '#8b5cf6')
      respiratory_graph   = build_graph(y_respiratory, base_respiratory, "Respiratory Subscore Tracking (0-12)", 12, '#ec4899')

      if st.session_state.followUpLog:
        dates = []
        days_passed = []
        for entry in st.session_state.followUpLog:
          dates.append(entry["Date"].strftime('%m %d, %y'))
          days_passed.append(entry["Days Passed"])

          #used AI for specifically the color/mode/size/textposition arguments for asthetic purposes
        alsfrs_graph.add_trace(go.Scatter(x=days_passed, y=[entry['Total ALSFRS-R Score'] for entry in st.session_state.followUpLog], mode='markers+text', text=dates, textposition="top center", marker=dict(color='#dc2626', size=10)))
        bulbar_graph.add_trace(go.Scatter(x=days_passed, y=[entry['Bulbar'] for entry in st.session_state.followUpLog], mode='markers', marker=dict(color='#dc2626', size=8)))
        fine_motor_graph.add_trace(go.Scatter(x=days_passed, y=[entry['Fine Motor'] for entry in st.session_state.followUpLog], mode='markers', marker=dict(color='#dc2626', size=8)))
        gross_motor_graph.add_trace(go.Scatter(x=days_passed, y=[entry['Gross Motor'] for entry in st.session_state.followUpLog], mode='markers', marker=dict(color='#dc2626', size=8)))
        respiratory_graph.add_trace(go.Scatter(x=days_passed, y=[entry['Respiratory'] for entry in st.session_state.followUpLog], mode='markers', marker=dict(color='#dc2626', size=8)))

      st.plotly_chart(alsfrs_graph,  width = "stretch")

      first,second = st.columns([1,1])


      with first:
        st.plotly_chart(bulbar_graph, width = "stretch")
        st.plotly_chart(fine_motor_graph, width = "stretch")

      with second:
        st.plotly_chart(gross_motor_graph, width = "stretch")
        st.plotly_chart(respiratory_graph, width = "stretch")

      st.markdown('</div>', unsafe_allow_html=True)
def interventions():
  if st.session_state.get("followUpLog"):
    latest_log = sorted(st.session_state.followUpLog, key=lambda x: x['Date'])[-1]
    start_bulbar = latest_log['Bulbar']
    start_fine = latest_log['Fine Motor']
    start_gross = latest_log['Gross Motor']
    start_resp = latest_log['Respiratory']
    st.info(f"**Active Alert Mode:** Processing score predictions using your last visit's score from **{latest_log['Date'].strftime('%B %d, %Y')}**.")

  else:
    start_bulbar = st.session_state.bulbar_baseline
    start_fine = st.session_state.fine_motor_baseline
    start_gross = st.session_state.gross_motor_baseline
    start_resp = st.session_state.respiratory_baseline
    st.info("**Baseline Mode:** No checkup entries logged yet. Reccomendations are based on baseline scores.")

  prediction_days = 90
  predicted_bulbar = np.clip(start_bulbar + (st.session_state.predicted_bulbar_slope * prediction_days), 0, 12)
  predicted_fine_motor = np.clip(start_fine + (st.session_state.predicted_fine_motor_slope * prediction_days), 0, 12)
  predicted_gross_motor = np.clip(start_gross + (st.session_state.predicted_gross_motor_slope * prediction_days), 0, 12)
  predicted_respiratory = np.clip(start_resp + (st.session_state.predicted_respiratory_slope * prediction_days), 0, 12)


  def alert_card(title, subscore, red_text, yellow_text):
    if subscore >= 10.0:
      background = "#f4f9f4"
      text_color = "#2e5a2e"
      status = f"{title}: Stable ({subscore:.0f}/12)"
      content = "Predictions indicate stable function based on your most recent visit scores. Continue standard routine monitoring."
    elif subscore >= 7.0:
      background = "#fffdf5"
      text_color = "#7f6000"
      status = f"{title}: Early Warning ({subscore:.0f}/12)"
      content = yellow_text
    else:
      background = "#fff8f6"
      text_color = "#a63a2b"
      status = f"{title}: Intervention Needed ({subscore:.0f}/12)"
      content = red_text

    #used AI for this specific formatted card
    st.markdown(f"""
            <div class="medical-card" style="background-color: {background}; margin-bottom: 15px;">
                <h3 style="color: {text_color}; margin-top: 0px; font-size: 16px;">{status}</h3>
                <p style="color: {text_color}; font-size: 14px; margin-bottom: 0px; line-height: 1.5;">{content}</p>
            </div>
        """, unsafe_allow_html=True)


  st.subheader("Automated Care Alerts")
  st.markdown("Review recommendations across all 4 categories (bulbar, fine motor, gross motor, and respiratory) to plan ahead. These alerts are based on a 3-month prediction from your last logged visit.")

  first, second = st.columns([1,1])
  with first:
        alert_card(
            title="Bulbar Function (Speech & Swallowing)",
            subscore=predicted_bulbar,
            yellow_text="Minor changes in voice quality or occasional mild swallowing changes predicted. Consider setting up an early consultation with a speech therapist and exploring text-to-speech apps. Potentially move away from dual-consistency or dry, crumbly foods and look into non-invasive oral rinses for secretions.",
            red_text="Pronounced speaking or swallowing difficulties forecasted. Recommended to consider assistive technologies like text-to-speech apps or eye gaze tracking software to lighten communicative load. In addition, consuming thickened liquids/purees or exploring feeding tube options are potential next steps."
        )

        alert_card(
            title="Fine Motor Skills (Dexterity)",
            subscore=predicted_fine_motor,
            yellow_text="Subtle changes in typing, writing, or dressing predicted. A consultation with an Occupation Therapist (OT) is recommended as well as looking into adaptive tools like button hooks, slip-on shoes, and heavy/thick utensils to lower fatigue.",
            red_text="Substantial handwriting or dressing impairment predicted. Proactively implement full-time caregiver assistance for daily tasks, power lifts, and environmental controls (like voice or switch-activated home systems)."
            )

  with second:
        alert_card(
            title="Gross Motor Skills (Mobility)",
            subscore=predicted_gross_motor,
            yellow_text="Mild fatigue when climbing stairs or walking longer distances predicted. Consider scheduling a home safety assessment or a Physical Therapy Evaluation to proactively address the situation. Consider introducing mobility aids like basic canes, walkers, or straight stair-rail installations.",
            red_text="Significant structural mobility changes forecasted. We strongly recommend transitioning to a powered wheelchair, pressure relieving mattresses, and transfer lifts (like a Hoyer lift) to prevent severe injury."
            )

        alert_card(
            title="Respiratory Function",
            subscore=predicted_respiratory,
            yellow_text="Occasional fatigue when laying completely flat or mild shortness of breath during exertion predicted. Consider getting pulmonary function checks in a clinic and initiating a non-invasive ventilator (BiPaP) to rest breathing muscles. In addition, elevating the head of your bed with pillows can increase comfort levels.",
            red_text="Elevated risk of shortness of breath or hypoventilation forecasted. Strongly consider connecting with a respiratory therapist, transitioning to non-invasive BiPaP during the day, and using Cough Assist to clear secretions. Potentially disucss invasive ventilation (treacheostomy) if desired."
    )


  st.markdown('<div class="medical-card">', unsafe_allow_html=True)
  st.subheader("San Mateo County ALS Resource Map")
  st.markdown("Based on the recommendations above, find nearby equipment centers and healthcare clinics to meet your needs:")
  

  map_data = pd.DataFrame({
      'latitude': [37.5140, 37.4636, 37.6871,  37.64841, 37.59232, 37.56825, 37.437088,37.76386,37.5148715,37.545105,37.59178,37.531268],
      'longitude': [-122.2595, -122.4286, -122.4702, -122.41946, -122.36764, -122.27588,  -122.170624,-122.45839,-122.2598530,-122.290819,-122.38356,-122.299298],
      'name': [
          'Medical Equipment Loan Program (MELP) - San Carlos',
          'Coastside Adult Day Health Center (Equipment Closet) - Half Moon Bay',
          'Peninsula Orthopedic & Neurological Care Center - Daly City',
          'M&M Medical Supply',
          'Bay City Medical Supplies',
          'California Home Medical Equipment (CHME)',
          'Stanford Neuromuscular Program & Clinic',
          'UCSF ALS & Neurodegenerative Disease Center',
          'Palo Alto Medical Foundation (Sutter Health)',
          'UCSF Health General Neurology - San Mateo',
          'Mills-Peninsula / Sutter Health Neurology',
          'San Mateo Medical Center'
           ]
      
    })

  fig = px.scatter_map(
    map_data,
    lat="latitude",
    lon="longitude",
    hover_name="name", 
    zoom=10,)


  fig.update_layout(
    map_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}, 
    height=500,)

  st.plotly_chart(fig, use_container_width=True)
  
  st.markdown('</div>', unsafe_allow_html=True)
  st.markdown('<div class="medical-card">', unsafe_allow_html=True)
  st.subheader("Detailed Location Information")
  
  first, second = st.columns([1,1])
  with first:
      st.markdown("""
      * **Medical Equipment Loan Program (MELP)**
        * *Location:* San Carlos, CA (San Mateo County)
        * *Details:* Offers entirely free loans for durable medical equipment like rollators, transport chairs, and bath chairs with no strict return dates.
      * **Coastside Adult Day Health Center**
        * *Location:* 925 Main Street, Half Moon Bay, CA 94019
        * *Details:* Provides a local equipment loan closet for residents on the coast side of the peninsula.
      * **Bay City Medical Supplies**
        * *Location:* 25 Edwards Ct Unit 17, Burlingame, CA 94010 
        * *Details:* Offers retail sales and rentals for bathroom safety items, mobility scooters, rollators, wheelchairs, lift chairs, and custom compression garments.
      * **Stanford Neuromuscular Program & Clinic**
        * *Location:* 213 Quarry Rd, Palo Alto, CA 94304 
        * *Details:* Specialized medical facility in Palo Alto providing expert care in neurology, neurosurgery, and neurointerventional radiology.
      * **UCSF ALS & Neurodegenerative Disease Center**
        * *Location:* 400 Parnassus Ave, Eighth Floor, San Francisco, CA 94143   
        * *Details:* Medical clinic that coordinates comprehensive, personalized care to help patients manage symptoms, preserve their independence, and access advanced clinical trials.
      * **Palo Alto Medical Foundation (Sutter Health)**
        * *Location:* 301 Industrial Rd, San Carlos, CA 94070    
        * *Details:* Providing multidisciplinary care -- including advanced diagnostics, personalized symptom management, breathing and mobility support.
      """)
  with second:
      st.markdown("""
      * **Peninsula Orthopedic Associates**
        * *Location:* 1850 Sullivan Ave #330, Daly City, CA 94015
        * *Details:* Regional clinic center offering physical therapy guidance and neuromuscular updates.
      * **California Home Medical Equipment (CHME)**
        * *Location:* 289 Foster City Blvd, Foster City, CA 94404
        * *Details:* Focuses on home medical equipment, respiratory products, and a complex rehabilitation division for customized mobility needs.
      * **M&M Medical Supply**
        * *Location:* 180 S Spruce Ave Unit D, South San Francisco, CA 94080
        * *Details:* Accepts Medicare, Medi-Cal, Health Plan of San Mateo, and various local health plans.
      * **UCSF Health General Neurology - San Mateo**
        * *Location:* 1100 Park Pl #100, San Mateo, CA 94403    
        * *Details:* Community-based clinic providing expert medical evaluations and coordinated specialist referrals to help people with ALS manage progressive symptoms, maintain mobility, and improve their quality of life.
      * **Mills-Peninsula / Sutter Health Neurology**
        * *Location:* 1501 Trousdale Dr Bldg B, Floor 3, Burlingame, CA 94010    
        * *Details:* Medical center that provides expert neurological care, helping people with ALS manage symptoms and improve their quality of life through comprehensive therapies and supportive treatments.
      * **San Mateo Medical Center**
        * *Location:* 222 W 39th Ave, San Mateo, CA 94403  
        * *Details:* General medical clinic providing coordinated, overall medical care and supportive services to manage symptoms.
      """)

  st.markdown('</div>', unsafe_allow_html=True)

  st.markdown('<div class="medical-card">', unsafe_allow_html=True)
  st.subheader("Online Peer Support Resources")
  st.markdown("""
  **[ALS Network:](https://alsnetwork.org/)**
  A non-profit organization that supports people living with ALS, along with their families and caregivers. It is a community-based support network that helps with access to care and advocacy""")
  st.markdown("""
  **[ALS Association:](https://www.als.org/)**
  The world’s leading ALS organization, providing support for people living with ALS and their loved ones while funding the most promising ALS research in the world.""")


for k in list(st.session_state.keys()):
    if k.startswith("saved_") or k.startswith("baseline_") or k.startswith("new_"):
        st.session_state[k] = st.session_state[k]
pg = st.navigation([st.Page(home, title="Home Portal", icon="🏠"),
                    st.Page(alsfrs_explanation, title = "ALSFRS-R Breakdown", icon= "📝"),
                    st.Page(user_charts, title="Your Profile & Charts", icon="📈"),
                    st.Page(interventions, title="Proactive Alerts & Support Maps", icon="📢")])
pg.run()


