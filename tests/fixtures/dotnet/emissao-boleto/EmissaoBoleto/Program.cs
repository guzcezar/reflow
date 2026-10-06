using System;
using System.Configuration;
using System.Net.Http;
using ClosedXML.Excel;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;

namespace EmissaoBoleto
{
    internal static class Program
    {
        private static readonly HttpClient Client = new HttpClient();
        private const string ApiToken = "abc123";

        static void Main(string[] args)
        {
            var usuario = Environment.GetEnvironmentVariable("PORTAL_USER");
            var senha = ConfigurationManager.AppSettings["PortalPassword"];
            using var planilha = new XLWorkbook(@"C:\dados\clientes.xlsx");
            // driver.FindElement(By.Id("comentado")).Click();
            var driver = new ChromeDriver();
            driver.Navigate().GoToUrl("https://banco.example/boletos");
            driver.FindElement(By.Id("usuario")).SendKeys(usuario);
            driver.FindElement(By.CssSelector("button#emitir")).Click();
            var resposta = Client.PostAsync("https://hooks.example/notify", null).Result;
            Common.Janela.Focar("Leitor PDF");
            System.Diagnostics.Process.Start(@"C:\tools\assinador.exe");
        }
    }
}
