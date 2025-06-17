<!doctype html>
<html lang="th">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;700&family=Inter:wght@400;700&display=swap" rel="stylesheet">
    
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

    <title>{% block title %}{% endblock %} - IOT Stock Chonburi</title>

    <link rel="icon" type="image/png" href="{{ url_for('static', filename='images/favicon.png') }}">
    <style>
        .flash-messages-container {
            position: fixed;
            top: 5rem;
            right: 1rem;
            z-index: 1050;
            width: auto;
            max-width: 400px;
        }
        .alert.fade-out {
            transition: opacity 0.5s ease-out;
            opacity: 0;
        }
    </style>

</head>
<body>
    <header>
        <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
            <div class="container-fluid">
                <a class="navbar-brand" href="{{ url_for('stock_overview') }}">IOT Stock Chonburi</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('stock_overview') }}">ภาพรวมสต็อก</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('stock_in') }}">รับสินค้าเข้า</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('stock_out') }}">เบิก-จ่ายอุปกรณ์</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('stock_return') }}">รับคืนสินค้า</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('manage_products') }}">จัดการสินค้าหลัก</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    </header>

    <div class="flash-messages-container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
    
    <main class="container-fluid mt-5 mb-5 pt-3">
        {% block content %}{% endblock %}
    </main>
    
    <footer class="footer">
        <div class="container">
            <span class="text-muted">IOT Stock Chonburi | พัฒนาโดย Artid Wiangkham</span>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
    
    {% block scripts %}{% endblock %}

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const flashMessages = document.querySelectorAll('.flash-messages-container .alert');

            flashMessages.forEach((message) => {
                setTimeout(() => {
                    message.classList.add('fade-out');
                    
                    message.addEventListener('transitionend', () => {
                        message.remove();
                    });

                }, 3000); 
            });
        });
    </script>
</body>
</html>
