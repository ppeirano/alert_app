<?php
$page_title = 'Dashboard';
require_once 'includes/db.php';
require_once 'includes/header.php';

$db = get_db();

// Active rules count
$active_rules = $db->query("SELECT COUNT(*) as cnt FROM alert_rules WHERE active = 1")->fetch()['cnt'];
$total_rules = $db->query("SELECT COUNT(*) as cnt FROM alert_rules")->fetch()['cnt'];

// Alerts sent today
$alerts_today = $db->query(
    "SELECT COUNT(*) as cnt FROM alert_log WHERE DATE(sent_at) = CURDATE()"
)->fetch()['cnt'];

// Total price checks today
$checks_today = $db->query(
    "SELECT COUNT(*) as cnt FROM price_history WHERE DATE(timestamp) = CURDATE()"
)->fetch()['cnt'];

// Last 10 alerts
$recent_alerts = $db->query(
    "SELECT al.*, ar.name as rule_name, ar.symbol
     FROM alert_log al
     JOIN alert_rules ar ON al.rule_id = ar.id
     ORDER BY al.sent_at DESC LIMIT 10"
)->fetchAll();

// Last prices per tracked symbol
$last_prices = $db->query(
    "SELECT p1.*
     FROM price_history p1
     INNER JOIN (
         SELECT symbol, MAX(timestamp) as max_ts
         FROM price_history
         GROUP BY symbol
     ) p2 ON p1.symbol = p2.symbol AND p1.timestamp = p2.max_ts
     ORDER BY p1.symbol"
)->fetchAll();
?>

<h2>Dashboard</h2>

<div class="row mb-4">
    <div class="col-md-4">
        <div class="card card-stat active-alerts">
            <div class="card-body">
                <h6 class="card-subtitle text-muted">Alertas Activas</h6>
                <h2><?= $active_rules ?> <small class="text-muted fs-6">/ <?= $total_rules ?> total</small></h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card card-stat triggered">
            <div class="card-body">
                <h6 class="card-subtitle text-muted">Alertas Enviadas Hoy</h6>
                <h2><?= $alerts_today ?></h2>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card card-stat total-checks">
            <div class="card-body">
                <h6 class="card-subtitle text-muted">Checks de Precio Hoy</h6>
                <h2><?= $checks_today ?></h2>
            </div>
        </div>
    </div>
</div>

<?php if ($last_prices): ?>
<div class="card mb-4">
    <div class="card-header"><i class="bi bi-currency-dollar"></i> Ultimos Precios</div>
    <div class="card-body p-0">
        <table class="table table-striped table-hover mb-0">
            <thead>
                <tr>
                    <th>Simbolo</th>
                    <th>Precio</th>
                    <th>Variacion</th>
                    <th>IV</th>
                    <th>Actualizado</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($last_prices as $p): ?>
                <tr>
                    <td><strong><?= htmlspecialchars($p['symbol']) ?></strong></td>
                    <td>$<?= number_format($p['precio'], 2, ',', '.') ?></td>
                    <td class="<?= $p['variacion'] >= 0 ? 'text-success' : 'text-danger' ?>">
                        <?= number_format($p['variacion'], 2) ?>%
                    </td>
                    <td><?= $p['iv'] ? number_format($p['iv'] * 100, 1) . '%' : '-' ?></td>
                    <td><?= $p['timestamp'] ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
<?php endif; ?>

<?php if ($recent_alerts): ?>
<div class="card">
    <div class="card-header"><i class="bi bi-bell"></i> Ultimas Alertas</div>
    <div class="card-body p-0">
        <table class="table table-striped table-hover mb-0">
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Regla</th>
                    <th>Simbolo</th>
                    <th>Precio</th>
                    <th>Mensaje</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($recent_alerts as $a): ?>
                <tr>
                    <td><?= $a['sent_at'] ?></td>
                    <td><?= htmlspecialchars($a['rule_name']) ?></td>
                    <td><strong><?= htmlspecialchars($a['symbol']) ?></strong></td>
                    <td>$<?= number_format($a['price_at_trigger'], 2, ',', '.') ?></td>
                    <td><small><?= htmlspecialchars($a['message']) ?></small></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
<?php else: ?>
<div class="alert alert-info">No hay alertas enviadas todavia.</div>
<?php endif; ?>

<?php require_once 'includes/footer.php'; ?>
