Imports System.Data.SqlClient
Imports System.Runtime.InteropServices
Imports System.Windows.Forms

Public Module Janela
    <DllImport("user32.dll")>
    Private Function FindWindow(lpClassName As String, lpWindowName As String) As IntPtr
    End Function

    Public Sub Focar(titulo As String)
        Dim handle = FindWindow(Nothing, titulo)
        SendKeys.SendWait("{ENTER}")
    End Sub

    Public Function Conectar() As SqlConnection
        Return New SqlConnection("Data Source=sql01;Initial Catalog=boletos;Password=S3nh@Forte")
    End Function
End Module
