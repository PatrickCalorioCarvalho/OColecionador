namespace OColecionadorBackEnd.Model
{
    public class Categoria
    {
        public int Id { get; set; }
        public required string Descricao { get; set; }
        public ICollection<Item>? Itens { get; set; }
    }
}
