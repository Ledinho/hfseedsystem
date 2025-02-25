function enviarEImprimir() {
  // Capturar os valores preenchidos no formulário
  const numeroFormulario = document.querySelector("h5 span").innerText;  // Seleciona o span dentro de h5
  const data = document.getElementById("data").value;
  const destino = document.getElementById("destino").value;
  const consultor = document.getElementById("consultor").value;
  const transportador = document.getElementById("transportador").value;
  const obs = document.getElementById("obs").value;
  const notas = Array.from(document.querySelectorAll('[name="nota[]"]')).map(nota => nota.value);

  function formatarData(data) {
    const dia = String(data.getDate()).padStart(2, '0'); // Obtém o dia e garante que tenha 2 dígitos
    const mes = String(data.getMonth() + 1).padStart(2, '0'); // Obtém o mês e garante que tenha 2 dígitos
    const ano = data.getFullYear(); // Ano
    const horas = String(data.getHours()).padStart(2, '0'); // Hora
    const minutos = String(data.getMinutes()).padStart(2, '0'); // Minutos
    const segundos = String(data.getSeconds()).padStart(2, '0'); // Segundos
    
    // Retorna a data e hora formatada
    return `${dia}/${mes}/${ano} ${horas}:${minutos}:${segundos}`;
  }

  const dataAtual = new Date();
  const dataFormatada = formatarData(dataAtual);

   // Organizar os dados para impressão
  const printWindow = window.open("", "_blank");  
  const imageUrl = "https://hfsementes.com.br/wp-content/uploads/2020/12/Logo-Vertical-HF-Sementes.png";  // URL da imagem

  const img = new Image();
  img.src = imageUrl;
  img.onload = function() {
  printWindow.document.write(`
    <html>
      <head>
        <title>Impressão de Fluxo NFe</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
          .notas-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
          .notas-container div { border: 1px solid black; padding: 5px; min-width: 100px; text-align: center; }
          .assinatura { margin-top: 30px; text-align: center; }
          .assinatura-line { margin-top: 10px; border-top: 1px solid black; width: 300px; margin: 0 auto; }
          .header {display: flex; align-items: center; margin-bottom: 30px;}
          .logo {display: inline-block; max-width: 80px; margin-right: 10px;}
          .header h1 {margin: 0; font-size: 24px; margin-left: 10px;}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <img src="${imageUrl}" class="logo" alt="Logo">
            <h1>Fluxo de Nota Fiscal Eletrônica ${numeroFormulario}</h1>
          </div>  
          <p><strong>Data:</strong> ${dataFormatada}</p>
          <p><strong>Destino:</strong> ${destino}</p>
          <p><strong>Consultor:</strong> ${consultor}</p>
          <p><strong>Transportador:</strong> ${transportador}</p>
          <p><strong>Observações:</strong> ${obs}</p>
          <h2>Notas Fiscais</h2>
          <div class="notas-container">
            ${notas.map(nota => `<div>${nota}</div>`).join("")}
          </div>
          <div class="assinatura">
            <div class="assinatura-line"></div>
            <p>Assinatura:</p>
          </div>
        </div>
      </body>
    </html>
  `);
  printWindow.document.close();
  printWindow.print();

  };

  // Retornar `true` para permitir o envio do formulário
  return true;
}
function enviarEImprimirDNFE() {
  // Capturar os valores preenchidos no formulário
  const numeroFormulario = document.querySelector("h5 span").innerText;  // Seleciona o span dentro de h5
  const data = document.getElementById("data").value;  // Data (já organizada)
  const consultor = document.getElementById("consultor").value;
  const entregue = document.getElementById("entregue").value;  // Campo "Entregue por"
  const obs = document.getElementById("obs").value;
  const notas = Array.from(document.querySelectorAll('[name="nota[]"]')).map(nota => nota.value);

  function formatarData(data) {
    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const ano = data.getFullYear();
    const horas = String(data.getHours()).padStart(2, '0');
    const minutos = String(data.getMinutes()).padStart(2, '0');
    const segundos = String(data.getSeconds()).padStart(2, '0');
  
    return `${dia}/${mes}/${ano} ${horas}:${minutos}:${segundos}`;
  }

  const dataAtual = new Date(data); // Usando o valor de data do campo do formulário
  const dataFormatada = formatarData(dataAtual);

  // Organizar os dados para impressão
  const printWindow = window.open("", "_blank");
  const imageUrl = "https://hfsementes.com.br/wp-content/uploads/2020/12/Logo-Vertical-HF-Sementes.png";  // URL da imagem

  printWindow.document.write(`
    <html>
      <head>
        <title>Impressão de Devolutiva DNFE</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
          .notas-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
          .notas-container div { border: 1px solid black; padding: 5px; min-width: 100px; text-align: center; }
          .assinatura { margin-top: 30px; text-align: center; }
          .assinatura-line { margin-top: 10px; border-top: 1px solid black; width: 300px; margin: 0 auto; }
          .header {display: flex; align-items: center; margin-bottom: 30px;}
          .logo {display: inline-block; max-width: 80px; margin-right: 10px;}
          .header h1 {margin: 0; font-size: 24px; margin-left: 10px;}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <img src="${imageUrl}" class="logo" alt="Logo">
            <h1>Fluxo de Nota Fiscal Eletrônica ${numeroFormulario}</h1>
          </div>
          <p><strong>Data:</strong> ${dataFormatada}</p>
          <p><strong>Consultor:</strong> ${consultor}</p>
          <p><strong>Entregue por:</strong> ${entregue}</p>
          <p><strong>Observações:</strong> ${obs}</p>
          <h2>Notas Fiscais</h2>
          <div class="notas-container">
            ${notas.map(nota => `<div>${nota}</div>`).join("")}
          </div>
          <div class="assinatura">
            <div class="assinatura-line"></div>
            <p>Assinatura:</p>
          </div>
        </div>
      </body>
    </html>
  `);

  // Esperar a imagem carregar antes de chamar a impressão
  const img = new Image();
  img.src = imageUrl;
  img.onload = function() {
    setTimeout(() => {
      printWindow.document.close();
      printWindow.print();
    },); // Atraso de 500ms para garantir que a imagem seja carregada antes de imprimir
  };

  // Retornar `true` para permitir o envio do formulário
  return true;
}
function imprimirDetalhes() {
  // Capturar os valores preenchidos no formulário
  const numeroFormulario = document.querySelector("h5 span").innerText;  // Seleciona o span dentro de h5
  const data = document.getElementById("data").value;  // Data (já organizada)
  const consultor = document.getElementById("consultor").value;
  const entregue = document.getElementById("entregue").value;  // Campo "Entregue por"
  const obs = document.getElementById("obs").value;
  const notas = Array.from(document.querySelectorAll('[name="nota[]"]')).map(nota => nota.value);

  function formatarData(data) {
    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const ano = data.getFullYear();
    const horas = String(data.getHours()).padStart(2, '0');
    const minutos = String(data.getMinutes()).padStart(2, '0');
    const segundos = String(data.getSeconds()).padStart(2, '0');
  
    return `${dia}/${mes}/${ano} ${horas}:${minutos}:${segundos}`;
  }

  const dataAtual = new Date(data); // Usando o valor de data do campo do formulário
  const dataFormatada = formatarData(dataAtual);

  // Organizar os dados para impressão
  const printWindow = window.open("", "_blank");
  const imageUrl = "https://hfsementes.com.br/wp-content/uploads/2020/12/Logo-Vertical-HF-Sementes.png";  // URL da imagem

  printWindow.document.write(`
    <html>
      <head>
        <title>Impressão de Devolutiva DNFE</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ccc; }
          .notas-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
          .notas-container div { border: 1px solid black; padding: 5px; min-width: 100px; text-align: center; }
          .assinatura { margin-top: 30px; text-align: center; }
          .assinatura-line { margin-top: 10px; border-top: 1px solid black; width: 300px; margin: 0 auto; }
          .header {display: flex; align-items: center; margin-bottom: 30px;}
          .logo {display: inline-block; max-width: 80px; margin-right: 10px;}
          .header h1 {margin: 0; font-size: 24px; margin-left: 10px;}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <img src="${imageUrl}" class="logo" alt="Logo">
            <h1>Fluxo de Nota Fiscal Eletrônica ${numeroFormulario}</h1>
          </div>
          <p><strong>Data:</strong> ${dataFormatada}</p>
          <p><strong>Consultor:</strong> ${consultor}</p>
          <p><strong>Entregue por:</strong> ${entregue}</p>
          <p><strong>Observações:</strong> ${obs}</p>
          <h2>Notas Fiscais</h2>
          <div class="notas-container">
            ${notas.map(nota => `<div>${nota}</div>`).join("")}
          </div>
          <div class="assinatura">
            <div class="assinatura-line"></div>
            <p>Assinatura:</p>
          </div>
        </div>
      </body>
    </html>
  `);

  // Esperar a imagem carregar antes de chamar a impressão
  const img = new Image();
  img.src = imageUrl;
  img.onload = function() {
    setTimeout(() => {
      printWindow.document.close();
      printWindow.print();
    },); // Atraso de 500ms para garantir que a imagem seja carregada antes de imprimir
  };

  // Retornar `true` para permitir o envio do formulário
  return true;
}