<?php
$page_title = 'Alertas';
require_once 'includes/db.php';
require_once 'includes/header.php';

$db = get_db();
$message = '';
$edit_rule = null;

// Handle actions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    if ($action === 'create' || $action === 'update') {
        $data = [
            'name' => trim($_POST['name'] ?? ''),
            'type' => $_POST['type'] ?? '',
            'symbol' => strtoupper(trim($_POST['symbol'] ?? '')),
            'mercado' => $_POST['mercado'] ?? 'bCBA',
            'direction' => $_POST['direction'] ?? 'any',
            'threshold' => floatval($_POST['threshold'] ?? 0),
            'underlying' => strtoupper(trim($_POST['underlying'] ?? '')) ?: null,
            'option_type' => $_POST['option_type'] ?? null,
            'strike' => $_POST['strike'] ? floatval($_POST['strike']) : null,
            'expiry' => $_POST['expiry'] ?? null,
            'condition' => $_POST['condition_field'] ?? null,
            'cooldown_minutes' => intval($_POST['cooldown_minutes'] ?? 60),
        ];

        if (empty($data['name']) || empty($data['type']) || empty($data['symbol'])) {
            $message = '<div class="alert alert-danger">Nombre, tipo y simbolo son obligatorios.</div>';
        } else {
            if ($action === 'create') {
                $stmt = $db->prepare(
                    "INSERT INTO alert_rules (name, type, symbol, mercado, direction, threshold,
                     underlying, option_type, strike, expiry, `condition`, cooldown_minutes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                );
                $stmt->execute([
                    $data['name'], $data['type'], $data['symbol'], $data['mercado'],
                    $data['direction'], $data['threshold'], $data['underlying'],
                    $data['option_type'], $data['strike'], $data['expiry'],
                    $data['condition'], $data['cooldown_minutes'],
                ]);
                $message = '<div class="alert alert-success">Alerta creada.</div>';
            } else {
                $rule_id = intval($_POST['rule_id']);
                $stmt = $db->prepare(
                    "UPDATE alert_rules SET name=?, type=?, symbol=?, mercado=?, direction=?,
                     threshold=?, underlying=?, option_type=?, strike=?, expiry=?,
                     `condition`=?, cooldown_minutes=? WHERE id=?"
                );
                $stmt->execute([
                    $data['name'], $data['type'], $data['symbol'], $data['mercado'],
                    $data['direction'], $data['threshold'], $data['underlying'],
                    $data['option_type'], $data['strike'], $data['expiry'],
                    $data['condition'], $data['cooldown_minutes'], $rule_id,
                ]);
                $message = '<div class="alert alert-success">Alerta actualizada.</div>';
            }
        }
    } elseif ($action === 'toggle') {
        $rule_id = intval($_POST['rule_id']);
        $active = intval($_POST['active']);
        $db->prepare("UPDATE alert_rules SET active = ? WHERE id = ?")->execute([$active, $rule_id]);
    } elseif ($action === 'delete') {
        $rule_id = intval($_POST['rule_id']);
        $db->prepare("DELETE FROM alert_rules WHERE id = ?")->execute([$rule_id]);
        $message = '<div class="alert alert-success">Alerta eliminada.</div>';
    }
}

// Load rule for editing
if (isset($_GET['edit'])) {
    $stmt = $db->prepare("SELECT * FROM alert_rules WHERE id = ?");
    $stmt->execute([intval($_GET['edit'])]);
    $edit_rule = $stmt->fetch();
}

// Get all rules
$rules = $db->query("SELECT * FROM alert_rules ORDER BY created_at DESC")->fetchAll();
?>

<h2>Alertas</h2>
<?= $message ?>

<!-- Form -->
<div class="card mb-4">
    <div class="card-header">
        <i class="bi bi-plus-circle"></i>
        <?= $edit_rule ? 'Editar Alerta' : 'Nueva Alerta' ?>
    </div>
    <div class="card-body">
        <form method="post">
            <input type="hidden" name="action" value="<?= $edit_rule ? 'update' : 'create' ?>">
            <?php if ($edit_rule): ?>
                <input type="hidden" name="rule_id" value="<?= $edit_rule['id'] ?>">
            <?php endif; ?>

            <div class="row mb-3">
                <div class="col-md-4">
                    <label class="form-label">Nombre</label>
                    <input type="text" name="name" class="form-control" required
                           value="<?= htmlspecialchars($edit_rule['name'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Tipo</label>
                    <select name="type" class="form-select" id="alertType" required>
                        <option value="price_pct_change" <?= ($edit_rule['type'] ?? '') === 'price_pct_change' ? 'selected' : '' ?>>Cambio Porcentual</option>
                        <option value="price_abs_change" <?= ($edit_rule['type'] ?? '') === 'price_abs_change' ? 'selected' : '' ?>>Cambio Absoluto</option>
                        <option value="iv_threshold" <?= ($edit_rule['type'] ?? '') === 'iv_threshold' ? 'selected' : '' ?>>Volatilidad Implicita</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Simbolo</label>
                    <input type="text" name="symbol" class="form-control" required
                           value="<?= htmlspecialchars($edit_rule['symbol'] ?? '') ?>"
                           placeholder="Ej: GGAL">
                </div>
            </div>

            <div class="row mb-3">
                <div class="col-md-3">
                    <label class="form-label">Mercado</label>
                    <select name="mercado" class="form-select">
                        <option value="bCBA" <?= ($edit_rule['mercado'] ?? 'bCBA') === 'bCBA' ? 'selected' : '' ?>>BCBA</option>
                        <option value="nYSE" <?= ($edit_rule['mercado'] ?? '') === 'nYSE' ? 'selected' : '' ?>>NYSE</option>
                        <option value="nASDAQ" <?= ($edit_rule['mercado'] ?? '') === 'nASDAQ' ? 'selected' : '' ?>>NASDAQ</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Direccion</label>
                    <select name="direction" class="form-select">
                        <option value="any" <?= ($edit_rule['direction'] ?? 'any') === 'any' ? 'selected' : '' ?>>Cualquiera</option>
                        <option value="up" <?= ($edit_rule['direction'] ?? '') === 'up' ? 'selected' : '' ?>>Sube</option>
                        <option value="down" <?= ($edit_rule['direction'] ?? '') === 'down' ? 'selected' : '' ?>>Baja</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Threshold</label>
                    <input type="number" name="threshold" class="form-control" step="0.01" required
                           value="<?= $edit_rule['threshold'] ?? '' ?>">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Cooldown (min)</label>
                    <input type="number" name="cooldown_minutes" class="form-control"
                           value="<?= $edit_rule['cooldown_minutes'] ?? 60 ?>">
                </div>
            </div>

            <!-- IV-specific fields -->
            <div id="ivFields" style="display: none;">
                <div class="row mb-3">
                    <div class="col-md-3">
                        <label class="form-label">Subyacente</label>
                        <input type="text" name="underlying" class="form-control"
                               value="<?= htmlspecialchars($edit_rule['underlying'] ?? '') ?>"
                               placeholder="Ej: GGAL">
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Tipo Opcion</label>
                        <select name="option_type" class="form-select">
                            <option value="call" <?= ($edit_rule['option_type'] ?? 'call') === 'call' ? 'selected' : '' ?>>Call</option>
                            <option value="put" <?= ($edit_rule['option_type'] ?? '') === 'put' ? 'selected' : '' ?>>Put</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Strike</label>
                        <input type="number" name="strike" class="form-control" step="0.01"
                               value="<?= $edit_rule['strike'] ?? '' ?>">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Vencimiento</label>
                        <input type="date" name="expiry" class="form-control"
                               value="<?= $edit_rule['expiry'] ?? '' ?>">
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Condicion</label>
                        <select name="condition_field" class="form-select">
                            <option value="above" <?= ($edit_rule['condition'] ?? 'above') === 'above' ? 'selected' : '' ?>>Sube de</option>
                            <option value="below" <?= ($edit_rule['condition'] ?? '') === 'below' ? 'selected' : '' ?>>Baja de</option>
                            <option value="either" <?= ($edit_rule['condition'] ?? '') === 'either' ? 'selected' : '' ?>>Cualquiera</option>
                        </select>
                    </div>
                </div>
            </div>

            <button type="submit" class="btn btn-primary">
                <i class="bi bi-check-lg"></i>
                <?= $edit_rule ? 'Actualizar' : 'Crear Alerta' ?>
            </button>
            <?php if ($edit_rule): ?>
                <a href="alerts.php" class="btn btn-secondary">Cancelar</a>
            <?php endif; ?>
        </form>
    </div>
</div>

<!-- Rules table -->
<div class="card">
    <div class="card-header"><i class="bi bi-list-ul"></i> Alertas Configuradas (<?= count($rules) ?>)</div>
    <div class="card-body p-0">
        <?php if ($rules): ?>
        <table class="table table-striped table-hover mb-0">
            <thead>
                <tr>
                    <th>Estado</th>
                    <th>Nombre</th>
                    <th>Tipo</th>
                    <th>Simbolo</th>
                    <th>Threshold</th>
                    <th>Cooldown</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($rules as $r): ?>
                <tr>
                    <td>
                        <form method="post" class="d-inline">
                            <input type="hidden" name="action" value="toggle">
                            <input type="hidden" name="rule_id" value="<?= $r['id'] ?>">
                            <input type="hidden" name="active" value="<?= $r['active'] ? 0 : 1 ?>">
                            <button type="submit" class="btn btn-sm <?= $r['active'] ? 'btn-success' : 'btn-secondary' ?>">
                                <?= $r['active'] ? 'Activa' : 'Inactiva' ?>
                            </button>
                        </form>
                    </td>
                    <td><?= htmlspecialchars($r['name']) ?></td>
                    <td>
                        <?php
                        $types = [
                            'price_pct_change' => 'Cambio %',
                            'price_abs_change' => 'Cambio $',
                            'iv_threshold' => 'IV',
                        ];
                        echo $types[$r['type']] ?? $r['type'];
                        ?>
                    </td>
                    <td><strong><?= htmlspecialchars($r['symbol']) ?></strong></td>
                    <td><?= $r['threshold'] ?></td>
                    <td><?= $r['cooldown_minutes'] ?> min</td>
                    <td>
                        <a href="?edit=<?= $r['id'] ?>" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <form method="post" class="d-inline"
                              onsubmit="return confirm('Eliminar esta alerta?')">
                            <input type="hidden" name="action" value="delete">
                            <input type="hidden" name="rule_id" value="<?= $r['id'] ?>">
                            <button type="submit" class="btn btn-sm btn-outline-danger">
                                <i class="bi bi-trash"></i>
                            </button>
                        </form>
                    </td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php else: ?>
        <div class="p-3 text-muted">No hay alertas configuradas. Crea una usando el formulario de arriba.</div>
        <?php endif; ?>
    </div>
</div>

<script>
function toggleIvFields() {
    const type = document.getElementById('alertType').value;
    document.getElementById('ivFields').style.display = type === 'iv_threshold' ? 'block' : 'none';
}
document.getElementById('alertType').addEventListener('change', toggleIvFields);
toggleIvFields();
</script>

<?php require_once 'includes/footer.php'; ?>
