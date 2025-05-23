# Textarea selectors for comments
TEXTAREA_SELECTORS = [
    '//textarea[@placeholder="Add a comment…"]',
    '//textarea[contains(@placeholder, "Add a comment")]',
    '//textarea[contains(@aria-label, "Add a comment")]',
]

# Post button selectors
POST_BUTTON_SELECTORS = [
    '//div[text()="Post"]/..',
    '//div[contains(text(), "Post")]/parent::div[@role="button"]',
    '//div[@class="x1i64zmx"]//div[@role="button"]',
    '//div[contains(@class, "x1i64zmx")]//div[@role="button"]',
]

# Like button selectors
LIKE_BUTTON_SELECTORS = [
    '//span[@class=""]//*[name()="svg"][@aria-label="Like"]',
    '//article//section//button//*[name()="svg"][@aria-label="Like"]',
    '//span[@aria-label="Like"]',
    '//button[@type="button"]//span[contains(@class, "")]//*[name()="svg"][@aria-label="Like"]',
    '//button[contains(@class, "")]//*[name()="svg"][@aria-label="Like"]',
]

# Save button selectors
SAVE_BUTTON_SELECTORS = [
    '//span[@class=""]//*[name()="svg"][@aria-label="Save"]',
    '//article//section//button//*[name()="svg"][@aria-label="Save"]',
    '//span[@aria-label="Save"]',
    '//button[@type="button"]//span[contains(@class, "")]//*[name()="svg"][@aria-label="Save"]',
    '//div[contains(@class, "")]//*[name()="svg"][@aria-label="Save"]',
]

# Profile button selectors
PROFILE_BUTTON_SELECTORS = [
    '//img[@alt="Profile picture"]/ancestor::a',
    "//nav//div[last()]//div[last()]//div[last()]//a",
    '//div[@role="tablist"]/a[last()]',
]

# Logout button selectors
LOGOUT_BUTTON_SELECTORS = [
    '//div[text()="Log out"]/..',
    '//button[contains(text(), "Log out")]',
    '//div[contains(text(), "Log out")]/..',
    '//div[contains(@role, "dialog")]//div[text()="Log out"]/..',
]
