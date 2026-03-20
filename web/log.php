<?php
$page_title = 'Log de Alertas';
require_once 'includes/db.php';
require_once 'includes/header.php';

$db = get_db();
$limit = intval($_GET['limit'] ?? 100);

$stmt = $db->prepare(
    "SELECT al.*, ar.name as rule_name, ar.symbol, ar.type as rule_type
     FROM alert_log al
     JOIN alert_rules ar ON al.rule_id = ar.id
     ORDER BY al.sent_at DESC LIMIT ?"
);
$stmt->execute([$limit]);
$logs = $stmt->fetchAll();
?>

<h2>Log de Alertas Enviadas</h2>

<?php if ($logs): ?>
<div class="card">
    <div class="card-header">
        <i class="bi bi-bell-fill"></i> Ultimas <?= count($logs) ?> alertas
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-striped table-hover mb-0">
                <thead>
                    <tr>
                        <th>Fecha/Hora</th>
                        <th>Regla</th>
                        <th>Simbolo</th>
                        <th>Tipo</th>
                        <th>Precio</th>
                        <th>Mensaje</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($logs as $l): ?>
                    <tr>
                        <td><?= $l['sent_at'] ?></td>
                        <td><?= htmlspecialchars($l['rule_name']) ?></td>
                        <td><strong><?= htmlspecialchars($l['symbol']) ?></strong></td>
                        <td>
                            <?php
                            $types = [
                                'price_pct_change' => '<span class="badge bg-primary">%</span>',
                                'price_abs_change' => '<span class="badge bg-info">$</span>',
                                'iv_threshold' => '<span class="badge bg-warning text-dark">IV</span>',
                            ];
                            echo $types[$l['rule_type']] ?? $l['rule_type'];
                            ?>
                        </td>
                        <td>$<?= number_format($l['price_at_trigger'], 2, ',', '.') ?></td>
                        <td><small><?= nl2br(htmlspecialchars($l['message'])) ?></small></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
<?php else: ?>
<div class="alert alert-info">No hay alertas enviadas todavia.</div>
<?php endif; ?>

<?php require_once 'includes/footer.php'; ?>
