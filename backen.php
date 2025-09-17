<?php
require_once('vendor/autoload.php');

use Facebook\WebDriver\Remote\RemoteWebDriver;
use Facebook\WebDriver\Remote\DesiredCapabilities;
use Facebook\WebDriver\WebDriverBy;
use Facebook\WebDriver\WebDriverExpectedCondition;
use Facebook\WebDriver\WebDriverKeys;
use Facebook\WebDriver\WebDriverWait;
use Facebook\WebDriver\Chrome\ChromeOptions;

// ====== Configuration ======
const DB_CONFIG = [
    'host'     => 'localhost',
    'user'     => 'root',
    'password' => '',
    'database' => 'freepik',
];
const EMAIL           = 'tuffailxhehzad@gmail.com';
const PASSWORD        = 'tuffail238';
const CHROMEDRIVER_URL = 'http://localhost:9515';
const LOGIN_URL       = 'https://www.freepik.com/login';
const COOKIES_FILE    = 'cookies.json';
const DOWNLOAD_DIR    = 'C:\\laragon\\www\\123\\downloads';
const CHROMEDRIVER_EXE = 'D:\\Downloads\\chromedriver-win64 (1)\\chromedriver-win64\\chromedriver.exe';

// ====== Logger ======
function log_msg($msg) {
    echo "[" . date("H:i:s") . "] $msg\n";
}

// ====== Init ChromeDriver ======
function init_driver(): RemoteWebDriver {
    log_msg("🚗 Starting ChromeDriver...");

    // Start ChromeDriver manually
    exec("start /B \"\" \"" . CHROMEDRIVER_EXE . "\" --port=9515");

    // Wait for ChromeDriver to start
    $start = microtime(true);
    while (!@fsockopen('localhost', 9515)) {
        if (microtime(true) - $start > 5) {
            die("❌ ChromeDriver didn't start in time.");
        }
        usleep(200000); // 0.2s
    }

    // Create download directory if it doesn't exist
    if (!is_dir(DOWNLOAD_DIR)) {
        mkdir(DOWNLOAD_DIR, 0777, true);
    }

    $options = new ChromeOptions();
    $prefs = [
        "download.default_directory" => DOWNLOAD_DIR,
        "download.prompt_for_download" => false,
        "download.directory_upgrade" => true,
        "safebrowsing.enabled" => true,
        "plugins.always_open_pdf_externally" => true,
        "profile.default_content_settings.popups" => 0,
    ];
    $options->setExperimentalOption("prefs", $prefs);
    $options->addArguments([
        '--no-sandbox',
        '--disable-dev-shm-usage',
        //'--headless'  // Optional
    ]);

    $capabilities = DesiredCapabilities::chrome();
    $capabilities->setCapability(ChromeOptions::CAPABILITY, $options);

    return RemoteWebDriver::create(CHROMEDRIVER_URL, $capabilities);
}

// ====== Cookie Handling ======
function save_cookies(RemoteWebDriver $driver): void {
    file_put_contents(COOKIES_FILE, json_encode($driver->manage()->getCookies()));
    log_msg("💾 Cookies saved.");
}

function load_cookies(RemoteWebDriver $driver): bool {
    if (!file_exists(COOKIES_FILE)) return false;

    $driver->get("https://www.freepik.com");
    $cookies = json_decode(file_get_contents(COOKIES_FILE), true);
    foreach ($cookies as $cookie) {
        unset($cookie['expiry']);
        $driver->manage()->addCookie($cookie);
    }
    log_msg("✅ Cookies loaded.");
    return true;
}

// ====== Login Handling ======
function login(RemoteWebDriver $driver, WebDriverWait $wait): void {
    if (load_cookies($driver)) return;

    log_msg("🔐 Manual login required.");
    $driver->get(LOGIN_URL);

    $wait->until(WebDriverExpectedCondition::elementToBeClickable(
        WebDriverBy::xpath("//span[text()='Continue with email']/parent::button")
    ))->click();

    $wait->until(WebDriverExpectedCondition::visibilityOfElementLocated(WebDriverBy::name("email")))
        ->sendKeys(EMAIL);

    $driver->findElement(WebDriverBy::name("password"))
        ->sendKeys(PASSWORD)
        ->sendKeys(WebDriverKeys::ENTER);

    echo "🧠 Solve CAPTCHA if prompted, then press Enter to continue...";
    fgets(STDIN);
    save_cookies($driver);
}

// ====== Database ======
function connect_db(): mysqli {
    $conn = new mysqli(...array_values(DB_CONFIG));
    if ($conn->connect_error) die("DB Error: " . $conn->connect_error);
    log_msg("🗄️ Connected to DB.");
    return $conn;
}

function get_pending_image(mysqli $conn): ? array {
    $result = $conn->query("SELECT * FROM downloads WHERE status = 0 LIMIT 1");
    return $result?->fetch_assoc() ?: null;
}

function mark_as_downloaded(mysqli $conn, int $id): void {
    $stmt = $conn->prepare("UPDATE downloads SET status = 1 WHERE id = ?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $stmt->close();
    log_msg("✅ Marked ID $id as downloaded.");
}

// ====== Image Downloader ======
function download_image(RemoteWebDriver $driver, WebDriverWait $wait, string $url): bool {
    log_msg("🌐 Visiting: $url");
    try {
        $driver->get($url);
        $downloadBtn = $wait->until(WebDriverExpectedCondition::elementToBeClickable(
            WebDriverBy::cssSelector("button[data-cy='download-button']")
        ));
        $driver->executeScript("arguments[0].scrollIntoView({block: 'center'});", [$downloadBtn]);
        usleep(500000);
        $downloadBtn->click();
        log_msg("📥 Download clicked.");
        sleep(20);
        return true;
    } catch (Exception $e) {
        log_msg("❌ Download failed: " . $e->getMessage());
        return false;
    }
}

// ====== Main Loop ======
function main(RemoteWebDriver $driver, WebDriverWait $wait, mysqli $conn): void {
    while (true) {
        $row = get_pending_image($conn);
        if ($row) {
            log_msg("🔄 Downloading ID: {$row['id']}");
            if (download_image($driver, $wait, $row['url'])) {
                mark_as_downloaded($conn, $row['id']);
            }
        } else {
            log_msg("⏳ No images. Waiting 20s...");
        }
        sleep(20);
    }
}

// ====== Entry Point ======
log_msg("🚀 Script started.");
$driver = init_driver();
register_shutdown_function(fn() => $driver->quit());

$wait = new WebDriverWait($driver, 20);
$conn = connect_db();
login($driver, $wait);
main($driver, $wait, $conn);
