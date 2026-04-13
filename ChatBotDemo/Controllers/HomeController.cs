using ChatBotDemo.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Reflection;
using System.Threading.Tasks;
using ChatBotDemo.Helpers;

using System.Text.Json;

namespace ChatBotDemo.Controllers
{
    public class HomeController : Controller
    {
        private static List<Usuario> usuarios = new List<Usuario>();
        private static List<Paciente> pacientes = new List<Paciente>();


        public IActionResult Index()
        {
            return RedirectToAction("Login");
        }

        // ================= LOGIN =================
        public IActionResult Login()
        {
            return View();
        }

        [HttpPost]
        public IActionResult Login(Usuario user)
        {
            var existe = usuarios.FirstOrDefault(u =>
                u.Email == user.Email && u.Password == user.Password);

            if (existe != null)
            {
                TempData["Email"] = user.Email;
                TempData["Password"] = user.Password;

                return RedirectToAction("Bienvenida");
            }

            ViewBag.Error = "Usuario o contraseña incorrectos";
            return View();
        }

        // ================= BIENVENIDA =================
        public IActionResult Bienvenida()
        {
            ViewBag.Email = TempData["Email"] ?? "-- @ --";
            return View();
        }

        // ================= REGISTRO =================
        public IActionResult Registro()
        {
            return View();
        }

        [HttpPost]
        public IActionResult Registro(Usuario user)
        {
            if (!ModelState.IsValid)
                return View(user);

            usuarios.Add(user);
            return RedirectToAction("Login");
        }

        // ================= PACIENTE =================
        public IActionResult RegistroPaciente()
        {
            return View();
        }

        [HttpPost]
        public IActionResult BuscarPaciente(string curp)
        {
            var paciente = pacientes.FirstOrDefault(c => c.CURP == curp);

            if (paciente != null)
            {
                TempData["CURP"] = paciente.CURP;
                TempData["Nombre"] = paciente.Nombre;
                TempData["Direccion"] = paciente.Direccion;
                return RedirectToAction("Chat");
            }

            ViewBag.Error = "paciente no encontrado";
            return View("RegistroPaciente");
        }

        [HttpPost]
        public IActionResult Guardarpaciente(Paciente paciente)
        {
            if (!ModelState.IsValid)
                return View("RegistroPaciente", paciente);

            pacientes.Add(paciente);

            TempData["Nombre"] = paciente.Nombre;
            TempData["Direccion"] = paciente.Direccion;
            TempData["CURP"] = paciente.CURP;

            return RedirectToAction("Chat");
        }

        // ================= CHAT =================
        public IActionResult Chat()
        {
            ViewBag.Nombre = TempData["Nombre"] ?? "Invitado";
            ViewBag.CURP = TempData["CURP"] ?? "N/A";
            ViewBag.Direccion = TempData["Direccion"] ?? "N/A";
            return View();
        }

        [HttpPost]
        public async Task<JsonResult> EnviarMensaje(string mensaje)
        {
            try
            {
                var respuestaIA = await ObtenerRespuestaIA(mensaje);

                if (!string.IsNullOrEmpty(respuestaIA))
                {
                    var respuestaFormateada = TextFormatter.FormatearRespuestaHtml(respuestaIA);
                    return Json(respuestaFormateada);
                }

                // fallback
                return Json(ObtenerRespuesta(mensaje));
            }
            catch
            {
                return Json(ObtenerRespuesta(mensaje));
            }
        }

        private string ObtenerRespuesta(string mensaje)
        {
            mensaje = mensaje.ToLower();

            if (mensaje.Contains("hola"))
                return "Hola 👋 ¿En qué puedo ayudarte?";
            if (mensaje.Contains("curp"))
                return "La CURP es tu clave única de registro poblacional.";
            if (mensaje.Contains("precio"))
                return "Nuestros servicios inician desde $100.";

            return "No entendí tu mensaje 🤖";
        }

        [HttpPost]
        public IActionResult BuscarPacienteMenu(string curp)
        {
            var paciente = pacientes.FirstOrDefault(c => c.CURP == curp);

            if (paciente != null)
            {
                TempData["CURP"] = paciente.CURP;
                TempData["Nombre"] = paciente.Nombre;
                TempData["Direccion"] = paciente.Direccion;
                return RedirectToAction("Chat");
            }

            ViewBag.Error = "paciente no encontrado";
            return View("RegistroPaciente");
        }

        public IActionResult CerrarSesion()
        {
            // Limpia sesión si usas Session
            //HttpContext.Session.Clear();

            // Limpia ViewBag indirectamente
            return RedirectToAction("Index");
        }


        // ================= IMPLEMENTACION DE UN MODELO DE IA =================
        // ----------------------- MÉTODO ASYNC PARA IA -----------------------
        private async Task<string> ObtenerRespuestaIA(string mensaje)
        {
            /*
             *  ERRORES QUE SE PUEDEN PRECENTAR EN EL USO DE HUGGINGS FACE
                # Error	    Significado
                429	        Te pasaste de requests
                402         quota	Sin créditos
                503	        Modelo ocupado
                404	        Modelo no disponible
             */

            var apiKey = "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";

            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");

                var body = new
                {
                    /*
                     * moonshotai/Kimi-K2-Instruct-0905
                     * mistralai/Mixtral-8x7B-Instruct-v0.1 ----------------
                     * mistralai/Mistral-7B-Instruct-v0.2 ------------------
                     * dphn/Dolphin-Mistral-24B-Venice-Edition -------------
                     * richardyoung/Mistral-7B-Instruct-v0.2-abliterated-obliteratus ---
                     * HuggingFaceH4/zephyr-7b-beta ------------------------
                     * google/flan-t5-base ---------------------------------
                     * bigscience/bloomz-560m ------------------------------
                     */
                    model = "moonshotai/Kimi-K2-Instruct-0905",
                    messages = new[]
                    {
                        new {
                            role = "user",
                            content = $"Eres un asistente médico en México. Responde en texto claro, con listas separadas por saltos de línea, sin usar markdown (** o -): {mensaje}"
                        }
                    }
                };

                var content = new StringContent(
                    JsonSerializer.Serialize(body),
                    Encoding.UTF8,
                    "application/json"
                );

                var response = await client.PostAsync(
                    "https://router.huggingface.co/v1/chat/completions",
                    content
                );

                var result = await response.Content.ReadAsStringAsync();

                Console.WriteLine(result);

                if (!response.IsSuccessStatusCode)
                    return "ERROR IA: " + result;

                try
                {
                    var jsonDoc = JsonDocument.Parse(result);

                    var respuesta = jsonDoc.RootElement
                        .GetProperty("choices")[0]
                        .GetProperty("message")
                        .GetProperty("content")
                        .GetString();

                    return respuesta;
                }
                catch
                {
                    return "Error procesando IA";
                }
            }
        }
    }
}
