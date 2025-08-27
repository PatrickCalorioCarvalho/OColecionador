namespace OColecionadorBackEnd.Model
{
    public class Item
    {
        public int Id { get; set; }
        public required string Nome { get; set; }
        public required int CategoriaId { get; set; }
        public Categoria? Categoria { get; set; }
        public ICollection<Foto>? Fotos { get; set; }
    }
}
