namespace ChatBotDemo.Helpers
{
    public static class TextFormatter
    {
        public static string FormatearRespuestaHtml(string texto)
        {
            if (string.IsNullOrEmpty(texto))
                return texto;

            texto = texto.Replace("**", "");
            texto = texto.Replace(" - ", "<br>• ");
            texto = texto.Replace("\n", "<br>");

            return texto;
        }
    }
}
