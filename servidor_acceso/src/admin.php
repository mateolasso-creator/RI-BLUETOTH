<?php
session_start();
if (!isset($_SESSION['loggedin'])) { header('Location: /index.php'); exit; }
$db = new mysqli('db', 'root', 'rootpassword', 'rfid_access');
$db->query("SET NAMES 'utf8'");

// Lógica de registro y conteos
$total_users = $db->query("SELECT COUNT(*) as total FROM users")->fetch_assoc()['total'];
$total_logs = $db->query("SELECT COUNT(*) as total FROM logs WHERE DATE(timestamp) = CURDATE()")->fetch_assoc()['total'];

if (isset($_POST['add_badge'])) {
    $token = $db->real_escape_string($_POST['new_token']);
    $name = $db->real_escape_string($_POST['user_name']);
    $db->query("INSERT INTO users (token, name) VALUES ('$token', '$name')");
    header("Location: admin.php");
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dashboard - Control de Acceso BT</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #f3f4f6;
            --sidebar: #111827;
            --primary: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
            --white: #ffffff;
        }

        body { font-family: 'Inter', sans-serif; background: var(--bg); margin: 0; display: flex; }
        
        /* Sidebar */
        .sidebar { width: 260px; background: var(--sidebar); height: 100vh; color: white; padding: 30px 20px; position: fixed; }
        .sidebar h2 { font-size: 1.2rem; color: var(--primary); margin-bottom: 40px; text-align: center; }
        .sidebar a { display: block; color: #9ca3af; text-decoration: none; padding: 12px; border-radius: 8px; margin-bottom: 10px; transition: 0.3s; }
        .sidebar a:hover, .sidebar a.active { background: #1f2937; color: white; }

        /* Main Content */
        .main { margin-left: 260px; padding: 40px; width: 100%; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        
        /* Cards */
        .stats-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .card-stat { background: var(--white); padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-left: 5px solid var(--primary); }
        .card-stat h3 { margin: 0; color: #6b7280; font-size: 0.9rem; text-transform: uppercase; }
        .card-stat p { margin: 10px 0 0; font-size: 1.8rem; font-weight: 600; color: #111827; }

        /* Tables & Sections */
        .section { background: var(--white); padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { text-align: left; background: #f9fafb; padding: 15px; color: #4b5563; font-weight: 600; border-bottom: 2px solid #f3f4f6; }
        td { padding: 15px; border-bottom: 1px solid #f3f4f6; color: #374151; }

        /* Badges */
        .badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
        .badge-success { background: #dcfce7; color: #166534; }
        .badge-danger { background: #fee2e2; color: #991b1b; }

        /* Forms */
        .form-group { display: flex; gap: 10px; margin-bottom: 20px; }
        input { padding: 12px; border: 1px solid #d1d5db; border-radius: 8px; flex: 1; outline: none; }
        input:focus { border-color: var(--primary); ring: 2px solid var(--primary); }
        .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: 0.3s; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: #2563eb; }
    </style>
</head>
<body>

<div class="sidebar">
    <h2>🔒 BT ACCESS</h2>
    <a href="#" class="active">📊 Dashboard</a>
    <a href="#usuarios">👥 Usuarios</a>
    <a href="#historial">📋 Historial</a>
    <br>
    <a href="?logout" style="color: var(--danger)">🚪 Cerrar Sesión</a>
</div>

<div class="main">
    <header>
        <h1>Panel de Control Bluetooth</h1>
        <span style="color: #6b7280"><?php echo date('d M, Y'); ?></span>
    </header>

    <div class="stats-container">
        <div class="card-stat">
            <h3>Total Usuarios</h3>
            <p><?php echo $total_users; ?></p>
        </div>
        <div class="card-stat" style="border-left-color: var(--success)">
            <h3>Accesos Hoy</h3>
            <p><?php echo $total_logs; ?></p>
        </div>
        <div class="card-stat" style="border-left-color: #f59e0b">
            <h3>Estado Servidor</h3>
            <p>ONLINE</p>
        </div>
    </div>

    <div class="section" id="usuarios">
        <h2>👥 Registro de Nuevo Token</h2>
        <form method="POST" class="form-group">
            <input type="text" name="new_token" placeholder="Ej: ABC-123-XYZ" required>
            <input type="text" name="user_name" placeholder="Nombre del Usuario" required>
            <button type="submit" name="add_badge" class="btn btn-primary">Añadir Usuario</button>
        </form>

        <table>
            <thead>
                <tr><th>ID</th><th>Token</th><th>Usuario</th><th>Estado</th></tr>
            </thead>
            <tbody>
                <?php
                $res = $db->query("SELECT * FROM users ORDER BY id DESC");
                while($u = $res->fetch_assoc()): ?>
                <tr>
                    <td>#<?php echo $u['id']; ?></td>
                    <td><code><?php echo $u['token']; ?></code></td>
                    <td><?php echo $u['name']; ?></td>
                    <td><span class="badge badge-success"><?php echo $u['status']; ?></span></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>

    <div class="section" id="historial">
        <h2>📋 Últimos Accesos</h2>
        <table>
            <thead>
                <tr><th>Token</th><th>Resultado</th><th>Fecha y Hora</th></tr>
            </thead>
            <tbody id="logs-body">
                <?php
                $logs = $db->query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 5");
                while($l = $logs->fetch_assoc()): ?>
                <tr>
                    <td><?php echo $l['token']; ?></td>
                    <td>
                        <span class="badge <?php echo ($l['access_status'] == 'GRANTED' || $l['access_status'] == 'Permitido') ? 'badge-success' : 'badge-danger'; ?>">
                            <?php echo $l['access_status']; ?>
                        </span>
                    </td>
                    <td><?php echo $l['timestamp']; ?></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
</div>

</body>
</html>