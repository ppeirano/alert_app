<?php
$page_title = 'Historial';
require_once 'includes/db.php';
require_once 'includes/header.php';

$db = get_db();

// Get distinct symbols
$symbols = $db->query(
    "SELECT DISTINCT symbol FROM price_history ORDER BY symbol"
)->fetchAll(PDO::FETCH_COLUMN);

$selected_symbol = $_GET['symbol'] ?? ($symbols[0] ?? '');
$date_from = $_GET['date_from'] ?? date('Y-m-d', strtotime('-7 days'));
$date_to = $_GET['date_to'] ?? date('Y-m-d');
$limit = intval($_GET['limit'] ?? 200);

$history = [];
if ($selected_symbol) {
    $stmt = $db->prepare(
        "SELECT * FROM price_history
         WHERE symbol = ? AND timestamp >= ? AND timestamp <= CONCAT(?, ' 23:59:59')
         ORDER BY timestamp DESC LIMIT " . $limit
    );
    $stmt->execute([$selected_symbol, $date_from, $date_to]);
    $history = $stmt->fetchAll();
}
?>

<h2>Historial de Precios</h2>

<div class="card mb-4">
    <div class="card-body">
        <form method="get" class="row g-3">
            <div class="col-md-3">
                <label class="form-label">Simbolo</label>
                <select name="symbol" class="form-select">
                    <?php foreach ($symbols as $s): ?>
                    <option value="<?= htmlspecialchars($s) ?>" <?= $s === $selected_symbol ? 'selected' : '' ?>>
                        <?= htmlspecialchars($s) ?>
                    </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Desde</label>
                <input type="date" name="date_from" class="form-control" value="<?= $date_from ?>">
            </div>
            <div class="col-md-3">
                <label class="form-label">Hasta</label>
                <input type="date" name="date_to" class="form-control" value="<?= $date_to ?>">
            </div>
            <div class="col-md-2">
                <label class="form-label">Limite</label>
                <input type="number" name="limit" class="form-control" value="<?= $limit ?>">
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="submit" class="btn btn-primary w-100">
                    <i class="bi bi-search"></i>
                </button>
            </div>
        </form>
    </div>
</div>

<?php if ($history): ?>
<div class="card">
    <div class="card-header">
        <i class="bi bi-clock-history"></i>
        <?= htmlspecialchars($selected_symbol) ?> - <?= count($history) ?> registros
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-striped table-hover table-sm mb-0">
                <thead>
                    <tr>
                        <th>Fecha/Hora</th>
                        <th>Precio</th>
                        <th>Variacion</th>
                        <th>Apertura</th>
                        <th>Maximo</th>
                        <th>Minimo</th>
                        <th>Cierre Ant.</th>
                        <th>Volumen</th>
                        <th>IV</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($history as $h): ?>
                    <tr>
                        <td><?= $h['timestamp'] ?></td>
                        <td><strong>$<?= number_format($h['precio'], 2, ',', '.') ?></strong></td>
                        <td class="<?= ($h['variacion'] ?? 0) >= 0 ? 'text-success' : 'text-danger' ?>">
                            <?= $h['variacion'] !== null ? number_format($h['variacion'], 2) . '%' : '-' ?>
                        </td>
                        <td><?= $h['apertura'] ? '$' . number_format($h['apertura'], 2, ',', '.') : '-' ?></td>
                        <td><?= $h['maximo'] ? '$' . number_format($h['maximo'], 2, ',', '.') : '-' ?></td>
                        <td><?= $h['minimo'] ? '$' . number_format($h['minimo'], 2, ',', '.') : '-' ?></td>
                        <td><?= $h['cierre_anterior'] ? '$' . number_format($h['cierre_anterior'], 2, ',', '.') : '-' ?></td>
                        <td><?= $h['volumen'] ? number_format($h['volumen'], 0, ',', '.') : '-' ?></td>
                        <td><?= $h['iv'] ? number_format($h['iv'] * 100, 1) . '%' : '-' ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
<?php elseif ($selected_symbol): ?>
<div class="alert alert-info">No hay datos para <?= htmlspecialchars($selected_symbol) ?> en el rango seleccionado.</div>
<?php else: ?>
<div class="alert alert-info">No hay datos de precios todavia. El motor de alertas los grabara automaticamente.</div>
<?php endif; ?>

<?php require_once 'includes/footer.php'; ?>
