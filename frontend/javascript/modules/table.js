/* global $ */
import DataTable from "datatables.net-bs";

export default class Table {
  constructor(table) {
    this.table = new DataTable(table)
  }
}
