using System.ComponentModel.DataAnnotations;

namespace ChatBotDemo.Models
{
    public class Paciente
    {
        //[StringLength(18, MinimumLength = 18, ErrorMessage = "La CURP debe tener 18 caracteres")]
        [Required(ErrorMessage = "La CURP es obligatoria")]
        public string CURP { get; set; }
        [Required(ErrorMessage = "El nombre es obligatorio")]
        public string Nombre { get; set; }
        [Required(ErrorMessage = "La dirección es obligatoria")]
        public string Direccion { get; set; }
    }
}
