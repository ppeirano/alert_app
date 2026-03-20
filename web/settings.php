<?php
$page_title = 'Configuracion';
require_once 'includes/db.php';
require_once 'includes/header.php';

$db = get_db();
$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $fields = [
        'iol_username', 'iol_password',
        'telegram_bot_token', 'telegram_chat_id',
        'risk_free_rate', 'poll_interval_minutes',
    ];
    foreach ($fields as $field) {
        if (isset($_POST[$field])) {
            save_setting($field, trim($_POST[$field]));
        }
    }
    $message = '<div class="alert alert-success">Configuracion guardada.</div>';
}

// Load current settings
$settings = [];
$rows = $db->query("SELECT key_name, value FROM settings")->fetchAll();
foreach ($rows as $row) {
    $settings[$row['key_name']] = $row['value'];
}
?>

<h2>Configuracion</h2>
<?= $message ?>

<form method="post">
    <div class="card mb-4">
        <div class="card-header"><i class="bi bi-key"></i> Invertir Online</div>
        <div class="card-body">
            <div class="row mb-3">
                <div class="col-md-6">
                    <label class="form-label">Usuario IOL</label>
                    <input type="text" name="iol_username" class="form-control"
                           value="<?= htmlspecialchars($settings['iol_username'] ?? '') ?>">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Password IOL</label>
                    <input type="password" name="iol_password" class="form-control"
                           value="<?= htmlspecialchars($settings['iol_password'] ?? '') ?>">
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header"><i class="bi bi-telegram"></i> Telegram</div>
        <div class="card-body">
            <div class="row mb-3">
                <div class="col-md-6">
                    <label class="form-label">Bot Token</label>
                    <input type="text" name="telegram_bot_token" class="form-control"
                           value="<?= htmlspecialchars($settings['telegram_bot_token'] ?? '') ?>"
                           placeholder="123456:ABC-DEF...">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Chat ID</label>
                    <input type="text" name="telegram_chat_id" class="form-control"
                           value="<?= htmlspecialchars($settings['telegram_chat_id'] ?? '') ?>">
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header"><i class="bi bi-gear"></i> Motor de Alertas</div>
        <div class="card-body">
            <div class="row mb-3">
                <div class="col-md-6">
                    <label class="form-label">Tasa Libre de Riesgo (anualizada, para calculo IV)</label>
                    <input type="number" name="risk_free_rate" class="form-control" step="0.01"
                           value="<?= htmlspecialchars($settings['risk_free_rate'] ?? '0.40') ?>">
                    <div class="form-text">Ej: 0.40 = 40%. Usado para calcular volatilidad implicita.</div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Intervalo de Poll (minutos)</label>
                    <input type="number" name="poll_interval_minutes" class="form-control"
                           value="<?= htmlspecialchars($settings['poll_interval_minutes'] ?? '2') ?>">
                    <div class="form-text">Cada cuantos minutos consultar precios (requiere reiniciar motor).</div>
                </div>
            </div>
        </div>
    </div>

    <button type="submit" class="btn btn-primary">
        <i class="bi bi-check-lg"></i> Guardar Configuracion
    </button>
</form>

<?php require_once 'includes/footer.php'; ?>
