# src/generate_dataset.py
"""
Synthetic generator for job + scholarship dataset (fake & real).
Produces: src/data/generated_dataset.csv and train/val/test splits.

Usage:
    python src/generate_dataset.py

Notes:
- This is synthetic data for development + testing.
- To improve realism, merge with real datasets (Kaggle, GitHub) later.
"""
import random
import csv
import os
from datetime import datetime, timedelta

OUT_DIR = "src/data"
OUT_FILE = os.path.join(OUT_DIR, "sample_offers.csv")
TRAIN_FILE = os.path.join(OUT_DIR, "train.csv")
VAL_FILE = os.path.join(OUT_DIR, "val.csv")
TEST_FILE = os.path.join(OUT_DIR, "test.csv")

# Adjust total_samples if you want >5000
TOTAL_SAMPLES = 6000  # script will dedupe and balance — expect >=5000 final

random.seed(42)

# Helper lists for variety
companies = [
    "Acme Labs", "GlobalTech", "NextGen Research", "Horizon University", "BrightPath",
    "Nova Scholarships", "Apex Solutions", "Greenfield Institute", "Stellar Corp", "BlueOak"
]

positions = [
    "Research Assistant", "Software Engineer", "Data Scientist Intern", "Product Manager",
    "Lab Technician", "Graduate Teaching Assistant", "Marketing Executive", "Backend Developer",
    "Full Stack Developer", "UX Designer"
]

scholarship_titles = [
    "Merit-based Scholarship", "Graduate Research Scholarship", "International Study Grant",
    "Need-based Fellowship", "STEM Excellence Award", "Women in Tech Scholarship"
]

fake_signals = [
    "pay fee", "processing fee", "send bank details", "click here to claim",
    "urgent response required", "limited seats - pay", "instant approval", "no interview",
    "wire transfer", "provide account number", "claim now", "prize awarded"
]

real_signals = [
    "interview scheduled", "application review", "attached position description",
    "formal offer letter", "onboarding details", "stipend details", "please confirm availability",
    "selection committee", "reference check", "official email from domain"
]

benefits_phrases = [
    "monthly stipend of ${amt}", "health benefits", "transport allowance", "accommodation provided",
    "research funding", "competitive salary", "tuition waiver", "mentorship and training"
]

email_domains = ["@acme.com", "@globaltech.org", "@university.edu", "@horizon.edu", "@novascholarships.org", "@gmail.com"]

sample_bodies_job_real = [
    "We are pleased to invite you to the interview for the {position} role at {company}. Please reply to schedule.",
    "{company} has completed the review of your application and would like to offer you the position of {position}. An official offer letter will follow.",
    "Thank you for applying to {company}. We would like to set up a technical interview for the {position} position. Please confirm your availability.",
    "Your profile matches our requirements for the {position}. The selection committee will reach out with next steps."
]

sample_bodies_scholarship_real = [
    "Congratulations — you have been shortlisted for the {title} by {company}. Please find attached the offer details and stipend information.",
    "The scholarship committee at {company} reviewed your application and recommends awarding the {title}. Please submit required documents.",
    "We are delighted to inform you that you have been selected for the {title}. Further instructions will follow from the grants office."
]

sample_bodies_job_fake = [
    "Congratulations! You have been selected for a high-paying {position} role. To claim, pay the processing fee now.",
    "Urgent: You have been approved for the {position}. Provide bank details and pay $30 to unlock your account.",
    "Instant job offer for {position}. No interview required. Click here: {link} to accept and send personal details.",
]

sample_bodies_scholarship_fake = [
    "You won a scholarship of ${amt}! Provide your bank account to receive scholarship funds immediately.",
    "Limited time scholarship award for {title}. Click {link} to claim — pay a small processing fee.",
    "Exclusive scholarship approval for you. No documents required. Send account and ID to {email} for immediate transfer."
]

# utilities
def random_date_within(days=365):
    base = datetime.now()
    delta_days = random.randint(0, days)
    dt = base - timedelta(days=delta_days, hours=random.randint(0,23), minutes=random.randint(0,59))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def random_phone():
    return "{}-{}-{}".format(random.randint(600,999), random.randint(100,999), random.randint(1000,9999))

def random_email(name=None):
    if name:
        nm = name.lower().replace(" ", ".")
    else:
        nm = "applicant{}".format(random.randint(1000,9999))
    return nm + random.choice(email_domains)

def random_amount(min_amt=100, max_amt=5000):
    return random.choice([100,250,500,750,1000,1500,2000,2500,3000,5000])

def make_link():
    token = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=12))
    return "http://bit.ly/" + token

def compose_title(category, is_fake, position_or_title):
    if category == "job":
        if is_fake:
            return f"Immediate Hiring: {position_or_title} (No Interview)"
        else:
            return f"{position_or_title} - {random.choice(['Full-time','Internship','Part-time'])}"
    else:
        if is_fake:
            return f"Exclusive {position_or_title} Award - Claim Now"
        else:
            return f"{position_or_title} Application Result"

def build_sample(idx):
    """
    Create one sample: returns dict with required fields.
    We'll alternate generating fake/real roughly to ensure variety.
    """
    # choose category
    category = random.choice(["job", "scholarship"])

    # randomly set fake flag ~50/50
    is_fake = random.random() < 0.5

    company = random.choice(companies)
    position = random.choice(positions)
    schol_title = random.choice(scholarship_titles)

    title = compose_title(category, is_fake, position if category=="job" else schol_title)

    # content assembly
    if category == "job":
        if is_fake:
            template = random.choice(sample_bodies_job_fake)
            link = make_link() if "{link}" in template else ""
            amt = ""  # rarely amounts in job fake templates
            email = random_email(company)
            body = template.format(position=position, company=company, link=link, email=email, amt=amt)
        else:
            template = random.choice(sample_bodies_job_real)
            body = template.format(position=position, company=company, title="", amt="")
    else:
        if is_fake:
            template = random.choice(sample_bodies_scholarship_fake)
            link = make_link() if "{link}" in template else ""
            amt = random_amount()
            email = random_email(company)
            body = template.format(position=position, company=company, link=link, email=email, amt=amt, title=schol_title)
        else:
            template = random.choice(sample_bodies_scholarship_real)
            amt = random_amount()
            body = template.format(title=schol_title, company=company, amt=amt)

    # Add extra noise / signals to make it realistic
    noise_phrases = []
    # Add one or two "fake signals" occasionally if sample is fake (to ensure models can pick up)
    if is_fake and random.random() < 0.9:
        noise_phrases.append(random.choice(fake_signals))
    # Add one or possible real signal to real samples
    if not is_fake and random.random() < 0.6:
        noise_phrases.append(random.choice(real_signals))

    # Add benefits randomly for real ones
    if not is_fake and random.random() < 0.5:
        noise_phrases.append(random.choice(benefits_phrases).replace("${amt}", f"${random_amount()}"))

    # Compose final text: body + noise + contact + disclaimers
    contact_email = random_email(company)
    contact_phone = random_phone()
    link = make_link() if ("{link}" in (title+body) or random.random() < 0.08) else ""
    has_link = 1 if link else 0

    extra = ""
    if noise_phrases:
        extra = " ".join(["Note:"] + noise_phrases)

    # sometimes append formal footer for realism
    footer = ""
    if not is_fake and random.random() < 0.3:
        footer = f" For official communication use hr@{company.replace(' ', '').lower()}.edu."

    text = " ".join([body, extra, footer]).strip()

    # small random capitalization/noise
    if random.random() < 0.05:
        text = text.upper()
    if random.random() < 0.05:
        text = text + " !!!"

    created_at = random_date_within(365)
    amount_field = random_amount() if ("scholarship" in category or "scholarship" in title.lower()) else ""

    sample = {
        "id": idx,
        "category": category,
        "title": title,
        "text": text,
        "source": "synthetic",
        "created_at": created_at,
        "contact_email": contact_email,
        "contact_phone": contact_phone,
        "has_link": has_link,
        "link": link,
        "amount": amount_field,
        "label": "fake" if is_fake else "real",
        "is_fake": 1 if is_fake else 0
    }
    return sample

def generate_dataset(total=TOTAL_SAMPLES):
    os.makedirs(OUT_DIR, exist_ok=True)
    samples = []
    for i in range(1, total+1):
        samples.append(build_sample(i))

    # Deduplicate by text
    seen_texts = set()
    unique_samples = []
    for s in samples:
        tx = s["text"].strip().lower()
        if tx not in seen_texts:
            unique_samples.append(s)
            seen_texts.add(tx)

    # Balance classes: equal fake & real
    fake = [s for s in unique_samples if s["is_fake"] == 1]
    real = [s for s in unique_samples if s["is_fake"] == 0]
    minlen = min(len(fake), len(real))
    # limit to minlen*2 to keep balance, but ensure >=5000
    balanced = fake[:minlen] + real[:minlen]
    random.shuffle(balanced)

    # If balanced size < 5000, generate more synthetic to reach >=5000
    while len(balanced) < 5000:
        idx = len(balanced) + 1 + total
        s = build_sample(idx)
        # ensure dedupe
        if s["text"].strip().lower() not in seen_texts:
            seen_texts.add(s["text"].strip().lower())
            balanced.append(s)
    random.shuffle(balanced)

    # Save full CSV
    keys = ["id","category","title","text","source","created_at","contact_email","contact_phone","has_link","link","amount","label","is_fake"]
    with open(OUT_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in balanced:
            writer.writerow(r)

    # Create splits (80/10/10)
    total_final = len(balanced)
    n_train = int(total_final * 0.8)
    n_val = int(total_final * 0.1)
    train = balanced[:n_train]
    val = balanced[n_train:n_train+n_val]
    test = balanced[n_train+n_val:]
    # save splits
    def save_split(path, rows):
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
    save_split(TRAIN_FILE, train)
    save_split(VAL_FILE, val)
    save_split(TEST_FILE, test)

    print("Generated:", OUT_FILE)
    print("Samples:", total_final)
    print("Train/Val/Test:", len(train), len(val), len(test))
    return {
        "full": OUT_FILE,
        "train": TRAIN_FILE,
        "val": VAL_FILE,
        "test": TEST_FILE,
        "n_samples": total_final
    }

if __name__ == "__main__":
    generate_dataset()
