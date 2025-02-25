var dependentes = [{
	identificador: 13,
  nome: "Joana da Silva",
  idade: 12,
}];


function carregarDependentes(){
	let dependentes_container = document.querySelector("#dependentesContainer");
  		dependentes_container.innerHTML = "";
  dependentes.forEach((el)=>{
  	let identificador = el.identificador;
  	let nome = el.nome;
    let idade = el.idade;
    let dependente_container = `<div class="dependente" data-id="${identificador}">
    															<input class="nome" placeholder="Digite o nome" type="text" value="${nome}"/>
                                  <input class="idade" placeholder="Digite a idade" type="number" value="${idade}"/>
                                  <div class="action">
                                  	<a href="#" class="salvar">salvar 💾</a>
                                    <a href="#" class="remover">❌</a>
																	</div>
															  </div>`;
  	dependentes_container.innerHTML += dependente_container;
  });
  salvarDependentes();
  removerDependentes();
  travarOutros(false);
}

function removerDependentes(){
	document.querySelectorAll("#dependentesContainer .remover").forEach((el, i)=>{
  	el.addEventListener("click", ()=>{
  		dependentes.splice(i, 1);  	
      carregarDependentes();
    });
  });
}

function adicionarDependentes(){
  dependentes.push({identificador:"", nome:"", idade: ""});
  carregarDependentes();
  travarOutros(document.querySelector("#dependentesContainer > div:last-child"));
}

function salvarDependentes(){
		document.querySelectorAll("#dependentesContainer .salvar").forEach((el, i)=>{
  	el.addEventListener("click", ()=>{
      let identificador = el.parentElement.parentElement.getAttribute("data-id");
      let nome = el.parentElement.parentElement.querySelector(".nome").value;
      let idade = el.parentElement.parentElement.querySelector(".idade").value;
    	
      if(!nome.length || !idade.length){
      	alert("Nome e idade precisam ser preenchidos para salvar.");
        return false;
      }
  		dependentes.splice(i, 1, {identificador: identificador, nome: nome, idade: idade});
      carregarDependentes();
      travarOutros(false);
    });
  });
}

function travarOutros(element){
	if(element == false){
  	document.querySelectorAll(".dependentes button, .dependentes .container > div").forEach((el)=>{
    	el.classList.remove("disabled");
    });
    document.querySelector("#containerDados").innerHTML = "";
    return false;
  }
  document.querySelectorAll(".dependentes button, .dependentes .container > div").forEach((el)=>{
  	if(el != element){
    	el.classList.add("disabled");
    }
  });
}

//init
document.querySelector("#btnAdicionarDependentes").addEventListener("click", adicionarDependentes);
carregarDependentes();

//capturarDados
document.querySelector("#btnCapturarDados").addEventListener("click", ()=>{
	document.querySelector("#containerDados").innerHTML = JSON.stringify(dependentes, undefined, 4);
});