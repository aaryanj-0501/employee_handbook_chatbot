import re

def infer_policy_type(text:str)->str:
    POLICY_KEYWORDS={
        "Leave":["pto","paid time off","leave","holiday","vacation","sick","parental"],
        "Work From Home":["remote", "work from home","wfh","telecommute"],
        "Payroll":["salary","payroll","overtime","compensation","pay","wage"],
        "Conduct":["code of conduct","harassment","discipline","behavior","ethics"],
        "Security":["data protection","confidentiality","cyber","cybersecurity","password","internet"],
        "Benefits":["health insurance","benefits","retirement","wellness"]
    }
    return assign_keyword(text,POLICY_KEYWORDS)

def infer_section(text:str)->str:
    SECTION_KEYWORDS={
        "Introduction":["welcome","introduction","company overview","about us"],
        "Policies":["policies","regulations","rules","policeis"],
        "Procedures":["procedure","procedures","steps","process"],
        "Employee Benefits":["perks","employee benefits","compensation"],
        "Code of Conduct":["code of conduct","ethics","behavior","ethics"],
        "Health and Safety":["health","safety","emergency","workplace safety"]
    }
    return assign_keyword(text,SECTION_KEYWORDS)

def infer_location(text:str)->str:
    LOCATION_KEYWORDS={
        "Headquarters":["headquarters","corporate office","main office"],
        "Branch Office":["regional office","branch office"],
        "Remote":["work from home","remote","telecommute"],
        "On-site":["on-site","in-office","office"]
    }
    return assign_keyword(text,LOCATION_KEYWORDS)

def infer_employee_type(text:str)->str:
    EMPLOYEE_KEYWORDS={
        "Full-Time":["full-time","permanent","regular"],
        "Part-Time":["part-time","temporary","seasonal"],
        "Contractor":["contractor","freelancer","consultant"],
        "Intern":["intern","internship","trainee"]
    }
    return assign_keyword(text,EMPLOYEE_KEYWORDS)

def assign_keyword(text:str,keyword_dict:dict)->str:
    text=text.lower()
    for section,keywords in keyword_dict.items():
        for keyword in keywords:
            if re.search(r'\b'+re.escape(keyword)+r'\b',text):
                return section
    return "General"
