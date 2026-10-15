from app.schemas.questionnaire import QuestionOption, QuestionOut

INTEREST_OPTIONS = [
    QuestionOption(
        value="building",
        label="Building or fixing machines and gadgets",
        fields=["Engineering", "Technology"],
    ),
    QuestionOption(
        value="coding",
        label="Solving puzzles and writing computer programs",
        fields=["Technology", "Engineering", "Research"],
    ),
    QuestionOption(
        value="caring",
        label="Helping and caring for people who are unwell",
        fields=["Medical", "Healthcare", "Biology"],
    ),
    QuestionOption(
        value="leading",
        label="Leading teams and managing money",
        fields=["Management", "Business", "Commerce"],
    ),
    QuestionOption(
        value="designing",
        label="Drawing, writing or designing creative work",
        fields=["Design", "Media", "Arts"],
    ),
    QuestionOption(
        value="researching",
        label="Doing experiments and research",
        fields=["Research", "Science"],
    ),
    QuestionOption(
        value="teaching",
        label="Teaching and explaining ideas to others",
        fields=["Education", "Research"],
    ),
    QuestionOption(
        value="travel",
        label="Travelling and hosting guests",
        fields=["Hospitality", "Tourism"],
    ),
    QuestionOption(
        value="numbers",
        label="Working with numbers, data and accounts",
        fields=["Commerce", "Finance", "Data"],
    ),
    QuestionOption(
        value="law",
        label="Arguing, debating and studying rules",
        fields=["Law", "Civil Services"],
    ),
]

LOCATION_OPTIONS = [
    QuestionOption(value="anywhere", label="Anywhere in India"),
    QuestionOption(value="delhi", label="Delhi NCR"),
    QuestionOption(value="mumbai", label="Mumbai"),
    QuestionOption(value="bengaluru", label="Bengaluru"),
    QuestionOption(value="chennai", label="Chennai"),
    QuestionOption(value="kolkata", label="Kolkata"),
    QuestionOption(value="hyderabad", label="Hyderabad"),
    QuestionOption(value="pune", label="Pune"),
]

QUESTIONS = [
    QuestionOut(id="full_name", prompt="What is your full name?", type="text"),
    QuestionOut(id="age", prompt="How old are you?", type="number"),
    QuestionOut(
        id="category",
        prompt="Which category do you belong to?",
        type="select",
        options=[
            QuestionOption(value="General", label="General"),
            QuestionOption(value="EWS", label="EWS"),
            QuestionOption(value="OBC", label="OBC"),
            QuestionOption(value="SC", label="SC"),
            QuestionOption(value="ST", label="ST"),
        ],
    ),
    QuestionOut(
        id="state_of_residence",
        prompt="Which state do you live in?",
        type="text",
    ),
    QuestionOut(
        id="annual_family_income",
        prompt="What is your approximate annual family income in rupees?",
        type="number",
    ),
    QuestionOut(
        id="qualifying_degree",
        prompt="What is the highest degree you have completed or are studying?",
        type="select",
        options=[
            QuestionOption(value="12th", label="Class 12 (10+2)"),
            QuestionOption(value="bachelor", label="Bachelor's degree"),
            QuestionOption(value="master", label="Master's degree"),
        ],
    ),
    QuestionOut(
        id="overall_percentage",
        prompt="What is your overall percentage in that degree?",
        type="number",
    ),
    QuestionOut(
        id="graduation_year",
        prompt="In which year did you complete (or will you complete) it?",
        type="number",
    ),
    QuestionOut(
        id="interests",
        prompt="Which activities do you enjoy the most? Choose as many as you like.",
        type="multi",
        options=INTEREST_OPTIONS,
    ),
    QuestionOut(
        id="preferred_locations",
        prompt="Where would you prefer to study?",
        type="multi",
        options=LOCATION_OPTIONS,
    ),
    QuestionOut(
        id="career_interest_statement",
        prompt="In your own words, what kind of job or career would you love?",
        type="text",
    ),
]

INTEREST_FIELDS = {
    option.value: option.fields for option in INTEREST_OPTIONS
}
INTEREST_LABELS = {
    option.value: option.label for option in INTEREST_OPTIONS
}
